#!/usr/bin/env python3
"""
Simple parallel climate classification using OpenAI API.

This version loads all articles into memory and processes them with controlled concurrency.
Much simpler than the batching approach.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from dotenv import load_dotenv
from tqdm.asyncio import tqdm as async_tqdm
import openai

# Load environment variables
load_dotenv(override=True)


class ClimateClassification(BaseModel):
    """Structured output model for climate/energy classification."""
    
    is_climate_or_energy: bool = Field(
        description="True if the article is about climate change or energy, False otherwise"
    )
    justification: Optional[str] = Field(
        default=None,
        description="One sentence justification if the article is about climate or energy"
    )


class SimpleClimateClassifier:
    """Simple classifier that processes articles in parallel with controlled concurrency."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-5-nano-2025-08-07"):
        """Initialize the classifier."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        
        self.system_prompt = """You are an expert at classifying articles about climate change and energy topics.

Classify articles as being about climate change or energy if they discuss:
- Climate change, global warming, climate crisis, or climate impacts
- Greenhouse gas emissions, carbon emissions, or decarbonization
- Renewable energy (solar, wind, hydroelectric, geothermal, etc.)
- Energy policy, energy transition, or energy systems
- Climate policy, climate agreements (e.g., Paris Agreement), or climate governance
- Electric vehicles or clean transportation
- Carbon pricing, carbon markets, or emissions trading
- Climate adaptation or mitigation strategies
- Extreme weather events in the context of climate change

If the article IS about climate or energy, provide a one-sentence justification in English explaining why.
If the article is NOT about climate or energy, set is_climate_or_energy to False and omit the justification.

IMPORTANT: All justifications must be written in English, regardless of the article's language."""
    
    async def classify_one(self, text: str, max_retries: int = 3) -> ClimateClassification:
        """Classify a single article with retry logic."""
        for attempt in range(max_retries):
            try:
                completion = await self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"Classify the following article text:\n\n{text}"}
                    ],
                    response_format=ClimateClassification,
                    timeout=30.0
                )
                return completion.choices[0].message.parsed
                
            except (openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError) as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise RuntimeError(f"Failed after {max_retries} retries: {str(e)}")
            except Exception as e:
                raise RuntimeError(f"Classification error: {str(e)}")
    
    async def process_articles(
        self,
        input_file: str,
        output_file: str,
        text_fields: list[str] = ["title", "body"],
        id_field: str = "uri",
        max_concurrent: int = 10,
        resume: bool = True
    ):
        """
        Process all articles from a JSONL file with controlled concurrency.
        
        Args:
            input_file: Path to input JSONL file
            output_file: Path to output JSONL file (uri + classification only)
            text_fields: List of fields to combine for text input
            id_field: Field to use as unique identifier
            max_concurrent: Maximum concurrent API requests
            resume: Skip articles already in output file
        """
        print(f"📖 Loading articles from {input_file}...")
        
        # Load all articles
        articles = []
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line.strip())
                    
                    # Extract text
                    text_parts = [str(record.get(field, "")) for field in text_fields if record.get(field)]
                    text = " ".join(text_parts)
                    
                    if text.strip():
                        articles.append({
                            "id": record.get(id_field, f"unknown_{line_num}"),
                            "text": text
                        })
                except json.JSONDecodeError:
                    continue
        
        print(f"✅ Loaded {len(articles):,} articles")
        
        # Check which articles are already processed
        processed_ids = set()
        if resume and Path(output_file).exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        result = json.loads(line.strip())
                        processed_ids.add(result.get(id_field))
                    except json.JSONDecodeError:
                        continue
            print(f"🔄 Resuming: {len(processed_ids):,} already processed")
        
        # Filter to unprocessed articles
        to_process = [a for a in articles if a["id"] not in processed_ids]
        
        if not to_process:
            print("✅ All articles already processed!")
            return
        
        print(f"🚀 Processing {len(to_process):,} articles with {max_concurrent} concurrent requests...\n")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # Open output file for appending
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        async def classify_and_save(article: dict, pbar, outfile):
            """Classify one article and save result."""
            async with semaphore:
                try:
                    classification = await self.classify_one(article["text"])
                    result = {
                        id_field: article["id"],
                        "is_climate_or_energy": classification.is_climate_or_energy,
                        "justification": classification.justification
                    }
                except Exception as e:
                    result = {
                        id_field: article["id"],
                        "is_climate_or_energy": False,
                        "justification": None,
                        "error": str(e)
                    }
                
                # Write result immediately
                outfile.write(json.dumps(result) + '\n')
                outfile.flush()
                pbar.update(1)
        
        # Process all articles in parallel with progress bar
        with open(output_file, 'a', encoding='utf-8') as outfile:
            pbar = async_tqdm(total=len(to_process), desc="🔍 Classifying")
            
            tasks = [classify_and_save(article, pbar, outfile) for article in to_process]
            await asyncio.gather(*tasks)
            
            pbar.close()
        
        print(f"\n✅ Processing complete! Results saved to {output_file}")
        print(f"   Total processed: {len(articles):,} articles")


async def main():
    """Main entry point."""
    
    # Configuration
    INPUT_FILE = "data/climate_articles_keywords.jsonl"
    OUTPUT_FILE = "data/climate_articles_keywords_classified.jsonl"
    TEXT_FIELDS = ["title", "body"]
    MAX_CONCURRENT = 50
    
    print(f"""
📋 Configuration:
   Input:  {INPUT_FILE}
   Output: {OUTPUT_FILE}
   Text fields: {' + '.join(TEXT_FIELDS)}
   Concurrent requests: {MAX_CONCURRENT}
    """)
    
    classifier = SimpleClimateClassifier()
    
    await classifier.process_articles(
        input_file=INPUT_FILE,
        output_file=OUTPUT_FILE,
        text_fields=TEXT_FIELDS,
        id_field="uri",
        max_concurrent=MAX_CONCURRENT,
        resume=True
    )
    
    print("\n🎉 All done!")


if __name__ == "__main__":
    asyncio.run(main())

