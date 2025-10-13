#!/usr/bin/env python3
"""
DigitalOcean Spaces File Upload Script

This script uploads files to a DigitalOcean Spaces bucket using the S3-compatible API.
"""

import os
import sys
import requests
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class DigitalOceanSpaces:
    """DigitalOcean Spaces file upload manager."""
    
    def __init__(self, 
                 endpoint_url: Optional[str] = None,
                 access_key_id: Optional[str] = None,
                 secret_access_key: Optional[str] = None,
                 bucket_name: Optional[str] = None,
                 region: str = 'lon1'):
        """
        Initialize the DigitalOcean Spaces client.
        
        Args:
            endpoint_url: Spaces endpoint URL
            access_key_id: DigitalOcean Spaces access key
            secret_access_key: DigitalOcean Spaces secret key
            bucket_name: Name of the bucket
            region: DigitalOcean region (default: lon1)
        """
        self.endpoint_url = endpoint_url
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.bucket_name = bucket_name
        self.region = region
        self.client = None
        
        if not all([endpoint_url, access_key_id, secret_access_key, bucket_name]):
            self._load_credentials()
        
        self._create_client()
    
    def _load_credentials(self) -> None:
        """Load credentials from environment variables."""
        load_dotenv()
        
        # Load credentials from environment variables
        self.access_key_id = os.getenv('DO_SPACES_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('DO_SPACES_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('DO_SPACES_BUCKET_NAME', 'discourselab')
        self.region = os.getenv('DO_SPACES_REGION', 'lon1')
        
        # Construct endpoint URL (use generic regional endpoint to avoid bucket name duplication)
        self.endpoint_url = f"https://{self.region}.digitaloceanspaces.com"
        
        if not self.access_key_id or not self.secret_access_key:
            raise ValueError(
                "Missing credentials. Please set these environment variables:\n"
                "- DO_SPACES_ACCESS_KEY_ID\n"
                "- DO_SPACES_SECRET_ACCESS_KEY\n"
                "Optional:\n"
                "- DO_SPACES_BUCKET_NAME (default: discourselab)\n"
                "- DO_SPACES_REGION (default: lon1)"
            )
    
    def _create_client(self) -> None:
        """Create the boto3 S3 client for DigitalOcean Spaces."""
        try:
            self.client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region
            )
            print(f"✅ Connected to DigitalOcean Spaces: {self.endpoint_url}")
            
        except Exception as e:
            print(f"❌ Failed to create client: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test the connection to DigitalOcean Spaces.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # List buckets to test connection
            response = self.client.list_buckets()
            print(f"✅ Connection test successful!")
            print(f"📦 Available buckets: {[bucket['Name'] for bucket in response.get('Buckets', [])]}")
            return True
            
        except ClientError as e:
            print(f"❌ Connection test failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def upload_file(self, 
                   local_file_path: str, 
                   remote_folder: str = 'ninja-news',
                   remote_filename: Optional[str] = None) -> bool:
        """
        Upload a single file to DigitalOcean Spaces.
        
        Args:
            local_file_path: Path to the local file
            remote_folder: Folder name in the bucket (default: ninja-news)
            remote_filename: Name for the file in the bucket (default: same as local)
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        if not os.path.exists(local_file_path):
            print(f"❌ File not found: {local_file_path}")
            return False
        
        # Determine remote filename
        if remote_filename is None:
            remote_filename = os.path.basename(local_file_path)
        
        # Create the full remote path
        remote_path = f"{remote_folder}/{remote_filename}"
        
        try:
            print(f"📤 Uploading {local_file_path} to {remote_path}...")
            
            # Upload the file (this automatically creates the "folder" structure)
            # Make file public by setting ACL and ContentType
            file_extension = os.path.splitext(remote_path)[1].lower()
            content_type = 'image/jpeg' if file_extension in ['.jpg', '.jpeg'] else 'image/png' if file_extension == '.png' else 'application/octet-stream'
            
            self.client.upload_file(
                local_file_path,
                self.bucket_name,
                remote_path,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': content_type
                }
            )
            
            # Verify the upload succeeded by checking if the object exists
            try:
                self.client.head_object(Bucket=self.bucket_name, Key=remote_path)
                # Get the public URL using CDN endpoint (not the upload endpoint)
                cdn_endpoint = f"https://{self.bucket_name}.{self.region}.cdn.digitaloceanspaces.com"
                public_url = f"{cdn_endpoint}/{remote_path}"
                print(f"✅ Upload successful!")
                print(f"🔗 Public URL: {public_url}")
                return True
            except ClientError as verify_error:
                print(f"❌ Upload verification failed: {verify_error}")
                return False
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"❌ Upload failed (ClientError {error_code}): {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected upload error: {e}")
            return False
    
    def upload_directory(self, 
                        local_directory: str, 
                        remote_folder: str = 'ninja-news',
                        file_extensions: Optional[List[str]] = None) -> bool:
        """
        Upload all files from a local directory to DigitalOcean Spaces.
        
        Args:
            local_directory: Path to the local directory
            remote_folder: Folder name in the bucket (default: ninja-news)
            file_extensions: List of file extensions to upload (e.g., ['.txt', '.pdf'])
            
        Returns:
            bool: True if all uploads successful, False otherwise
        """
        if not os.path.exists(local_directory):
            print(f"❌ Directory not found: {local_directory}")
            return False
        
        if not os.path.isdir(local_directory):
            print(f"❌ Path is not a directory: {local_directory}")
            return False
        
        # Get all files in the directory
        files_to_upload = []
        for root, dirs, files in os.walk(local_directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Filter by file extension if specified
                if file_extensions:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext not in file_extensions:
                        continue
                
                files_to_upload.append(file_path)
        
        if not files_to_upload:
            print(f"📁 No files found to upload in {local_directory}")
            return True
        
        print(f"📁 Found {len(files_to_upload)} file(s) to upload...")
        
        success_count = 0
        for file_path in files_to_upload:
            # Calculate relative path for remote folder structure
            rel_path = os.path.relpath(file_path, local_directory)
            remote_filename = f"{remote_folder}/{rel_path}"
            
            if self.upload_file(file_path, remote_folder, rel_path):
                success_count += 1
        
        print(f"📊 Upload complete: {success_count}/{len(files_to_upload)} files uploaded successfully")
        return success_count == len(files_to_upload)
    
    def list_files(self, folder: str = 'ninja-news') -> List[str]:
        """
        List all files in a folder in the bucket.
        
        Args:
            folder: Folder name in the bucket
            
        Returns:
            List[str]: List of file names
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"{folder}/"
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Remove the folder prefix from the key
                    file_name = obj['Key'].replace(f"{folder}/", "", 1)
                    if file_name:  # Skip empty strings
                        files.append(file_name)
            
            if files:
                print(f"📋 Found {len(files)} file(s) in {folder}/:")
                for i, file in enumerate(files, 1):
                    print(f"  {i}. {file}")
            else:
                print(f"📋 No files found in {folder}/")
            
            return files
            
        except ClientError as e:
            print(f"❌ Failed to list files: {e}")
            return []
    
    def delete_file(self, remote_path: str) -> bool:
        """
        Delete a file from the bucket.
        
        Args:
            remote_path: Path to the file in the bucket (e.g., 'ninja-news/file.txt')
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            print(f"🗑️  Deleting {remote_path}...")
            self.client.delete_object(Bucket=self.bucket_name, Key=remote_path)
            print(f"✅ File deleted successfully!")
            return True
            
        except ClientError as e:
            print(f"❌ Failed to delete file: {e}")
            return False
    
    def download_file(self, 
                     public_url: str, 
                     local_file_path: Optional[str] = None,
                     folder: str = 'downloads') -> bool:
        """
        Download a file from its public URL.
        
        Args:
            public_url: Public URL of the file to download
            local_file_path: Local path to save the file (optional)
            folder: Folder to save downloads in (default: downloads)
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            # Create downloads folder if it doesn't exist
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"📁 Created downloads folder: {folder}")
            
            # Determine local file path
            if local_file_path is None:
                # Extract filename from URL
                filename = public_url.split('/')[-1]
                local_file_path = os.path.join(folder, filename)
            
            print(f"📥 Downloading from: {public_url}")
            print(f"💾 Saving to: {local_file_path}")
            
            # Download the file
            response = requests.get(public_url, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Get file size for progress tracking
            total_size = int(response.headers.get('content-length', 0))
            
            with open(local_file_path, 'wb') as file:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Show progress for large files
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\r📊 Download progress: {progress:.1f}%", end='', flush=True)
            
            print(f"\n✅ Download completed!")
            print(f"📁 File saved: {local_file_path}")
            
            # Show file size
            file_size = os.path.getsize(local_file_path)
            print(f"📏 File size: {self._format_file_size(file_size)}")
            
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"❌ Access denied (403 Forbidden). The file may not be publicly accessible.")
                print(f"💡 Try using download_file_from_bucket() instead for authenticated access.")
                return False
            else:
                print(f"❌ HTTP error: {e}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Download failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def download_file_from_bucket(self, 
                                 remote_path: str, 
                                 local_file_path: Optional[str] = None,
                                 folder: str = 'downloads') -> bool:
        """
        Download a file from the bucket using its remote path.
        
        Args:
            remote_path: Path to the file in the bucket (e.g., 'ninja-news/file.txt')
            local_file_path: Local path to save the file (optional)
            folder: Folder to save downloads in (default: downloads)
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            # Clean the remote path (remove full URL if provided)
            if remote_path.startswith('http'):
                # Extract the path part from the full URL
                url_parts = remote_path.replace(self.endpoint_url, '').lstrip('/')
                remote_path = url_parts
                print(f"🔧 Extracted bucket path: {remote_path}")
            
            # Create downloads folder if it doesn't exist
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"📁 Created downloads folder: {folder}")
            
            # Determine local file path
            if local_file_path is None:
                # Extract filename from remote path
                filename = os.path.basename(remote_path)
                local_file_path = os.path.join(folder, filename)
            
            print(f"📥 Downloading from bucket: {remote_path}")
            print(f"💾 Saving to: {local_file_path}")
            
            # Download using authenticated S3 client
            self.client.download_file(
                self.bucket_name,
                remote_path,
                local_file_path
            )
            
            print(f"✅ Download completed!")
            print(f"📁 File saved: {local_file_path}")
            
            # Show file size
            file_size = os.path.getsize(local_file_path)
            print(f"📏 File size: {self._format_file_size(file_size)}")
            
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                print(f"❌ File not found in bucket: {remote_path}")
                print(f"💡 Use list_files() to see available files in the bucket")
            elif error_code == 'AccessDenied':
                print(f"❌ Access denied to file: {remote_path}")
            else:
                print(f"❌ Download failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def download_folder(self, 
                       remote_folder: str = 'ninja-news',
                       local_folder: str = 'downloads',
                       file_extensions: Optional[List[str]] = None) -> bool:
        """
        Download all files from a folder in the bucket.
        
        Args:
            remote_folder: Folder name in the bucket (default: ninja-news)
            local_folder: Local folder to save downloads (default: downloads)
            file_extensions: List of file extensions to download (e.g., ['.txt', '.pdf'])
            
        Returns:
            bool: True if all downloads successful, False otherwise
        """
        try:
            # List files in the remote folder
            files = self.list_files(remote_folder)
            
            if not files:
                print(f"📋 No files found in {remote_folder}/")
                return True
            
            # Filter files by extension if specified
            if file_extensions:
                files = [f for f in files if any(f.lower().endswith(ext) for ext in file_extensions)]
                print(f"📁 Filtering to {len(files)} file(s) with extensions: {file_extensions}")
            
            if not files:
                print(f"📋 No files match the specified extensions")
                return True
            
            print(f"📥 Downloading {len(files)} file(s) from {remote_folder}/...")
            
            success_count = 0
            for file in files:
                remote_path = f"{remote_folder}/{file}"
                local_path = os.path.join(local_folder, file)
                
                if self.download_file_from_bucket(remote_path, local_path, local_folder):
                    success_count += 1
            
            print(f"📊 Download complete: {success_count}/{len(files)} files downloaded successfully")
            return success_count == len(files)
            
        except Exception as e:
            print(f"❌ Failed to download folder: {e}")
            return False
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            str: Formatted file size
        """
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def url_to_bucket_path(self, url: str) -> str:
        """
        Convert a DigitalOcean Spaces URL to a bucket path.
        
        Args:
            url: Full URL to the file
            
        Returns:
            str: Bucket path (e.g., 'ninja-news/file.txt')
        """
        if url.startswith(self.endpoint_url):
            return url.replace(self.endpoint_url, '').lstrip('/')
        else:
            # Try to extract from any DigitalOcean Spaces URL
            import re
            match = re.search(r'/([^/]+/[^/]+)$', url)
            if match:
                return match.group(1)
            else:
                raise ValueError(f"Could not extract bucket path from URL: {url}")
    
    def download_from_url(self, url: str, local_file_path: Optional[str] = None, folder: str = 'downloads') -> bool:
        """
        Download a file from a DigitalOcean Spaces URL (handles both public and private files).
        
        Args:
            url: Full URL to the file
            local_file_path: Local path to save the file (optional)
            folder: Folder to save downloads in (default: downloads)
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            # First try public download
            if self.download_file(url, local_file_path, folder):
                return True
        except:
            pass
        
        # If public download fails, try authenticated download
        try:
            bucket_path = self.url_to_bucket_path(url)
            return self.download_file_from_bucket(bucket_path, local_file_path, folder)
        except Exception as e:
            print(f"❌ Failed to download from URL: {e}")
            return False


def main():
    """Main function to test DigitalOcean Spaces connection and upload files."""
    print("🌊 DigitalOcean Spaces File Upload Test")
    print("=" * 50)
    
    try:
        # Create Spaces client
        spaces = DigitalOceanSpaces()
        
        # Test connection
        if not spaces.test_connection():
            sys.exit(1)
        
        print("\n" + "=" * 50)
        
        # List existing files
        print("📋 Listing existing files in ninja-news folder:")
        spaces.list_files('ninja-news')
        
        # Example: Upload a test file
        test_file = "test_upload.txt"
        if os.path.exists(test_file):
            print(f"\n📤 Uploading test file: {test_file}")
            spaces.upload_file(test_file, 'ninja-news')
        
        # Example: Upload data directory if it exists
        data_dir = "data"
        if os.path.exists(data_dir):
            print(f"\n📁 Uploading data directory: {data_dir}")
            spaces.upload_directory(data_dir, 'ninja-news')
        
        # Example: Download files from the bucket
        print(f"\n📥 Download examples:")
        
        # Download a specific file if it exists in the bucket
        files = spaces.list_files('ninja-news')
        if files:
            example_file = files[0]
            print(f"📥 Downloading example file: {example_file}")
            spaces.download_file_from_bucket(f'ninja-news/{example_file}', folder='downloads')
        
        # Example: Download from URL (handles both public and private files)
        example_url = f"{spaces.endpoint_url}/ninja-news/{example_file}" if files else None
        if example_url:
            print(f"\n📥 Downloading from URL: {example_url}")
            spaces.download_from_url(example_url, folder='downloads')
        
        # Download all files from ninja-news folder
        print(f"\n📁 Downloading all files from ninja-news folder:")
        spaces.download_folder('ninja-news', 'downloads')
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 To use this script, create a .env file with your DigitalOcean Spaces credentials:")
        print("DO_SPACES_ACCESS_KEY_ID=your_access_key")
        print("DO_SPACES_SECRET_ACCESS_KEY=your_secret_key")
        print("DO_SPACES_BUCKET_NAME=discourselab")
        print("DO_SPACES_REGION=lon1")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 