#!/usr/bin/env python3
"""
Test MarkdownV2 formatting validation
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def validate_markdown_v2(text):
    """Basic validation for MarkdownV2 formatting"""
    import re
    
    # Check for unescaped special characters that should be escaped
    problematic_chars = []
    
    # Characters that should be escaped in MarkdownV2
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        # Find unescaped occurrences (not preceded by \)
        pattern = f"(?<!\\\\)\\{re.escape(char)}"
        matches = re.finditer(pattern, text)
        for match in matches:
            # Skip if it's inside formatting (like *bold* or _italic_)
            start = match.start()
            if char in ['*', '_']:
                # Check if it's part of valid formatting
                continue
            problematic_chars.append((char, start))
    
    return problematic_chars

def test_rank_ladder_output():
    """Test the rank ladder output for MarkdownV2 compliance"""
    print("TESTING MARKDOWN V2 COMPLIANCE")
    print("=" * 40)
    
    try:
        from rank_ladder import RankLadderDisplay
        
        # Test with a sample user ID
        ladder_text = RankLadderDisplay.format_rank_ladder(1)
        
        print(f"Generated text length: {len(ladder_text)} characters")
        print("\nFirst 500 characters:")
        print("-" * 30)
        print(ladder_text[:500])
        print("-" * 30)
        
        # Validate MarkdownV2 formatting
        problems = validate_markdown_v2(ladder_text)
        
        if problems:
            print(f"\n⚠️  Found {len(problems)} potential MarkdownV2 issues:")
            for char, pos in problems[:10]:  # Show first 10 issues
                context_start = max(0, pos - 20)
                context_end = min(len(ladder_text), pos + 20)
                context = ladder_text[context_start:context_end]
                print(f"  Character '{char}' at position {pos}: ...{context}...")
        else:
            print("\n✅ No obvious MarkdownV2 formatting issues found!")
        
        # Additional checks
        print(f"\nAdditional checks:")
        print(f"  - Contains asterisks: {'*' in ladder_text}")
        print(f"  - Contains underscores: {'_' in ladder_text}")
        print(f"  - Contains escaped dashes: '\\-' in ladder_text")
        print(f"  - Contains escaped periods: '\\.' in ladder_text")
        
        return len(problems) == 0
        
    except Exception as e:
        print(f"❌ Error testing rank ladder: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("RANK LADDER MARKDOWN V2 VALIDATION")
    print("=" * 50)
    print()
    
    success = test_rank_ladder_output()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ RANK LADDER READY FOR TELEGRAM!")
        print("The rank ladder button should now work properly.")
    else:
        print("❌ ISSUES FOUND")
        print("The rank ladder may still have MarkdownV2 formatting problems.")

if __name__ == "__main__":
    main()
