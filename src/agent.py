import sys
from pathlib import Path
from openai import AzureOpenAI

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_engine import RAGEngine
from src.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_API_VERSION,
    TEMPERATURE,
    MAX_TOKENS
)

class ProcurementAgent:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_KEY,
            api_version=AZURE_API_VERSION
        )
        self.rag_engine = RAGEngine()
        self.deployment = AZURE_OPENAI_DEPLOYMENT
    
    def query(self, user_question, context_type="general"):
        """
        Main query method
        
        Args:
            user_question: User's question
            context_type: Type of context needed
        """
        # Retrieve relevant documents
        relevant_docs = self.rag_engine.retrieve(user_question, k=5)
        
        # Build context from retrieved documents
        context = "\n\n".join([doc['content'] for doc in relevant_docs])
        
        # Create system prompt
        system_prompt = f"""You are a Procurement Assistant for Bio Farma, an Indonesian pharmaceutical company.

Your role is to help with:
1. Creating Purchase Orders (POs)
2. Validating Invoices against POs
3. Comparing prices across suppliers and time periods

Use the following context from the procurement database:

{context}

Guidelines:
- Provide specific, actionable answers
- Always cite material codes, PO numbers, or supplier IDs when relevant
- For prices, always use Indonesian Rupiah (IDR) with proper formatting
- Flag any discrepancies or issues
- Be concise but thorough
"""
        
        # Call Azure OpenAI
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        return response.choices[0].message.content