#!/usr/bin/env python3

def test_extraction():
    clean_query = 'what is cac?'
    print('Clean query:', clean_query)
    
    # Handle common abbreviations first
    abbreviation_mappings = {
        'cac': 'customer acquisition cost',
        'ltv': 'lifetime value',
        'cpa': 'cost per acquisition',
        'cpc': 'cost per click',
        'cpm': 'cost per mille',
        'roi': 'return on investment',
        'kpi': 'key performance indicator'
    }
    
    # Check if the query is just an abbreviation
    for abbrev, full_term in abbreviation_mappings.items():
        print(f'Checking if "{clean_query.strip()}" == "{abbrev}"')
        if clean_query.strip() == abbrev:
            print(f'MATCH! Returning: {full_term}')
            return full_term
    
    print('No direct match, checking patterns...')
    
    import re
    
    # Patterns to extract terms from definition queries (more precise)
    patterns = [
        # Direct quotes
        r'["\']([^"\']+)["\']',
        # After "define" or "definition of"
        r'(?:define|definition of)\s+(.+?)(?:\s*\?|$)',
        # After "what is" or "how is"
        r'(?:what is|how is)\s+(.+?)(?:\s+defined|mean|means|\?|$)',
        # After "meaning of"
        r'meaning of\s+(.+?)(?:\s*\?|$)',
        # After "tell me about" or "explain"
        r'(?:tell me about|explain)\s+(.+?)(?:\s*\?|$)',
        # After "which assets use" or "what uses"
        r'(?:which assets use|what uses)\s+(.+?)(?:\s*\?|$)',
        # After "find" or "search for"
        r'(?:find|search for)\s+(.+?)(?:\s*\?|$)',
        # Handle abbreviations in context (e.g., "what is CAC")
        r'(?:what is|define|explain)\s+([A-Z]{2,4})(?:\s*\?|$)',
        # General term extraction (fallback)
        r'\b([A-Z][a-zA-Z\s]+(?:Cost|Revenue|Rate|Value|Metric|KPI|Data|Table|Column))\b'
    ]
    
    for i, pattern in enumerate(patterns):
        print(f'Testing pattern {i+1}: {pattern}')
        match = re.search(pattern, clean_query)
        if match:
            term = match.group(1).strip()
            print(f'Pattern {i+1} matched! Term: "{term}"')
            
            # Clean up the term
            term = re.sub(r'\s+', ' ', term)  # Normalize whitespace
            term = term.strip('?.,!')  # Remove punctuation
            print(f'Cleaned term: "{term}"')
            
            # Check if it's an abbreviation and expand it
            if len(term) <= 4 and (term.isupper() or term.islower()):
                print(f'Term "{term}" looks like an abbreviation, checking mappings...')
                for abbrev, full_term in abbreviation_mappings.items():
                    if term.lower() == abbrev:
                        print(f'Found abbreviation mapping: {term} -> {full_term}')
                        return full_term
            
            if len(term) > 2:  # Ensure it's not too short
                print(f'Returning term: "{term}"')
                return term
    
    print('No pattern matched, trying word extraction...')
    
    # If no pattern matches, try to extract any meaningful term
    words = clean_query.split()
    for word in words:
        if len(word) > 2 and not word in ['the', 'and', 'for', 'with', 'what', 'is', 'are', 'how', 'why', 'when', 'where']:
            print(f'Checking word: "{word}"')
            # Check if it's an abbreviation
            if (word.isupper() or word.islower()) and len(word) <= 4:
                for abbrev, full_term in abbreviation_mappings.items():
                    if word.lower() == abbrev:
                        print(f'Found abbreviation in word extraction: {word} -> {full_term}')
                        return full_term
            print(f'Returning word: "{word}"')
            return word
    
    print('No term found')
    return ""

if __name__ == "__main__":
    result = test_extraction()
    print(f'Final result: "{result}"') 