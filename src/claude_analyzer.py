#!/usr/bin/env python3
"""
Claude API Integration for Jira Description Generation

Uses Claude AI to analyze Zendesk ticket conversations and generate:
- Concise, accurate summary/title
- Structured Jira description with proper narrative flow
"""

import os
from typing import Dict, Optional, Tuple
from anthropic import Anthropic


class ClaudeAnalyzer:
    """Analyzes Zendesk tickets using Claude AI to generate Jira content."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude analyzer.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Latest Sonnet model

    def analyze_zendesk_ticket(
        self,
        zendesk_conversation: str,
        ticket_id: str,
        customer: str = "Unknown",
        product: str = "Redis Software"
    ) -> Tuple[str, str]:
        """
        Analyze Zendesk ticket and generate Jira summary + description.

        Args:
            zendesk_conversation: Full Zendesk ticket conversation text
            ticket_id: Zendesk ticket ID
            customer: Customer name
            product: Product name (e.g., "Redis Software", "Redis Cloud")

        Returns:
            Tuple of (summary, description)
        """
        prompt = self._build_analysis_prompt(
            zendesk_conversation,
            ticket_id,
            customer,
            product
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            temperature=0,  # Deterministic for consistency
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Parse response to extract summary and description
        return self._parse_response(response.content[0].text)

    def _build_analysis_prompt(
        self,
        conversation: str,
        ticket_id: str,
        customer: str,
        product: str
    ) -> str:
        """Build the analysis prompt for Claude."""
        return f"""You are analyzing a Zendesk support ticket to create a Jira bug report for {product} engineering team.

**Zendesk Ticket #{ticket_id}**
**Customer:** {customer}
**Product:** {product}

**Full Ticket Conversation:**
```
{conversation}
```

---

**Your Task:**

Analyze this Zendesk conversation and generate:

1. **Summary (one-line title)**
   - Concise, technical summary of the ACTUAL issue (not the original ticket title)
   - Format: "[Customer] - [Component/ROOT CAUSE] [specific technical issue] causing [PRIMARY IMPACT]"
   - Examples:
     - "FedEx - CRDB slave OVC higher than master causing local and inter-CRDB replication failure"
     - "Wells Fargo - node_mgr crash due to missing system_user_password after upgrade"
   - Focus on ROOT CAUSE and PRIMARY IMPACT (not secondary symptoms like memory discrepancy)
   - Omit technical details like hash slot ranges, specific values, etc. - save for description
   - If the ticket evolved (e.g., started as "support package request" but became "CRDB issue"), use the evolved issue

2. **Structured Description**

Use this format with markdown headers (##):

## Problem Statement
[2-3 sentence overview of the issue and its impact]
[If customer has operational constraints (peak freeze, maintenance windows, business-critical periods), mention them here]

## Error Observed
[Specific error messages, symptoms, or anomalies - use code blocks for logs]

## Impact
[Bullet points of impact: service state, data risk, customer operations, etc.]

## Root Cause Analysis
[If known: technical explanation of why this occurred - FOCUS ON CAUSAL RELATIONSHIPS]
[Clearly distinguish: ROOT CAUSE → PRIMARY EFFECT → SECONDARY CONSEQUENCES]
[Example: "OVC corruption (root cause) → local replication failure (primary) → inter-CRDB sync blocked + memory discrepancy (secondary)"]
[If unknown: "Investigation in progress" or "Requires R&D analysis"]

## Reproduction Steps
[If reproduction steps are provided in the conversation: include FULL details with actual commands and outputs]
[Use numbered steps with code blocks showing exact commands, outputs, and observations]
[Example format:
1. Created test environment: `command here`
   ```
   actual output here
   ```
2. Observed behavior: description
   ```
   evidence/logs here
   ```
]
[If not reproducible or no reproduction provided: skip this section]

## Workaround Applied
[If available: solution that was applied, with commands/steps]
[If proposed but pending: clearly state why (e.g., "Customer in peak freeze period", "Requires maintenance window")]
[If no workaround: "No confirmed workaround available"]

## Technical Details
[Key technical information: version numbers, cluster/node IDs, affected components, OVC values, etc.]
[Use code blocks for technical data]

## Related Information
[Related tickets, Slack threads, similar issues mentioned]

## Ask From R&D
[Numbered list of investigation/fix steps needed]

---

**Important Guidelines:**
- Extract the NARRATIVE from the conversation (Problem → Investigation → Solution)
- Use technical precision (exact error messages, version numbers, component names)
- Use code blocks for logs, commands, output
- Use bullet points for lists
- Be concise - focus on facts for R&D, not the support conversation flow
- If the ticket is still under investigation, say so explicitly
- Highlight any unusual findings (e.g., "restart worked in test but failed in prod")

**Output Format:**

Return your response in this exact format:

SUMMARY: [one-line summary here]

DESCRIPTION:
[structured description here]
"""

    def _parse_response(self, response_text: str) -> Tuple[str, str]:
        """
        Parse Claude's response to extract summary and description.

        Args:
            response_text: Claude's response text

        Returns:
            Tuple of (summary, description)
        """
        lines = response_text.strip().split('\n')

        summary = ""
        description = ""
        in_description = False

        for line in lines:
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("DESCRIPTION:"):
                in_description = True
                continue
            elif in_description:
                description += line + "\n"

        # Clean up description
        description = description.strip()

        # Fallback if parsing fails
        if not summary:
            summary = "Unable to parse summary"
        if not description:
            description = response_text

        return summary, description

    def estimate_cost(self, conversation_length: int) -> float:
        """
        Estimate API cost for analyzing a conversation.

        Args:
            conversation_length: Length of conversation in characters

        Returns:
            Estimated cost in USD
        """
        # Rough estimate: 1 token ≈ 4 characters
        # Claude Sonnet 4: $3/MTok input, $15/MTok output
        # Assume 2000 chars input prompt overhead, 2000 tokens output

        input_tokens = (len(conversation_length) + 2000) / 4
        output_tokens = 2000

        input_cost = (input_tokens / 1_000_000) * 3.00
        output_cost = (output_tokens / 1_000_000) * 15.00

        return input_cost + output_cost


def main():
    """Test the Claude analyzer with sample text."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python claude_analyzer.py <zendesk_pdf_path>")
        sys.exit(1)

    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Export your API key: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    # Parse the PDF
    from universal_ticket_parser import parse_ticket_file

    pdf_path = sys.argv[1]
    print(f"Analyzing: {pdf_path}")

    ticket_data = parse_ticket_file(pdf_path)
    conversation = ticket_data.get('description', '')
    ticket_id = ticket_data.get('ticket_id', 'Unknown')

    print(f"Conversation length: {len(conversation)} chars")

    # Estimate cost
    analyzer = ClaudeAnalyzer()
    cost = analyzer.estimate_cost(len(conversation))
    print(f"Estimated cost: ${cost:.4f}")

    # Analyze
    print("\nAnalyzing with Claude AI...")
    summary, description = analyzer.analyze_zendesk_ticket(
        conversation,
        ticket_id,
        customer="FedEx",  # Would extract from ticket
        product="Redis Software"
    )

    print("\n" + "="*80)
    print("GENERATED SUMMARY")
    print("="*80)
    print(summary)
    print()

    print("="*80)
    print("GENERATED DESCRIPTION")
    print("="*80)
    print(description)


if __name__ == "__main__":
    main()
