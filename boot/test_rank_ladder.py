#!/usr/bin/env python3
"""
Script to test the rank ladder functionality
"""

import sqlite3
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DB_PATH

def check_rank_definitions():
    """Check what's in the rank_definitions table"""
    print("CHECKING RANK DEFINITIONS TABLE:")
    print("-" * 40)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rank_definitions ORDER BY rank_id")
        ranks = cursor.fetchall()
        
        if ranks:
            for rank in ranks:
                print(f"  Rank {rank[0]}: {rank[1]} {rank[2]} ({rank[3]}-{rank[4] if rank[4] else '∞'} points)")
        else:
            print("  No ranks found in database!")
            print("  Inserting default ranks...")
            
            # Insert default ranks
            cursor.execute('''
            INSERT OR REPLACE INTO rank_definitions (rank_id, rank_name, rank_emoji, min_points, max_points, special_perks, is_special)
            VALUES 
                (1, 'Freshman', '🥉', 0, 99, '{}', 0),
                (2, 'Sophomore', '🥈', 100, 249, '{}', 0),
                (3, 'Junior', '🥇', 250, 499, '{}', 0),
                (4, 'Senior', '🏆', 500, 999, '{"daily_confessions": 8}', 0),
                (5, 'Graduate', '🎓', 1000, 1999, '{"daily_confessions": 10, "priority_review": true}', 0),
                (6, 'Master', '👑', 2000, 4999, '{"daily_confessions": 15, "priority_review": true, "comment_highlight": true}', 1),
                (7, 'Legend', '🌟', 5000, NULL, '{"all_perks": true, "unlimited_daily": true, "legend_badge": true}', 1)
            ''')
            conn.commit()
            print("  Default ranks inserted!")
    print()

def test_rank_ladder_display():
    """Test the RankLadderDisplay functionality"""
    print("TESTING RANK LADDER DISPLAY:")
    print("-" * 35)
    
    try:
        # Import the rank ladder module
        from rank_ladder import RankLadderDisplay
        
        # Test getting all ranks
        ranks = RankLadderDisplay.get_all_ranks()
        print(f"  Found {len(ranks)} ranks")
        
        # Test formatting rank ladder for a test user (ID 1)
        ladder_text = RankLadderDisplay.format_rank_ladder(1)
        print(f"  Generated ladder text ({len(ladder_text)} characters)")
        print("  Preview:")
        print("  " + ladder_text[:200] + "..." if len(ladder_text) > 200 else "  " + ladder_text)
        
        return True
        
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_ranking_integration():
    """Check if the ranking integration is working"""
    print("CHECKING RANKING INTEGRATION:")
    print("-" * 35)
    
    try:
        from ranking_integration import ranking_manager
        
        # Try to get a user rank (this will create one if it doesn't exist)
        test_user_id = 1
        user_rank = ranking_manager.get_user_rank(test_user_id)
        
        if user_rank:
            print(f"  Test user {test_user_id} rank: {user_rank.rank_name} {user_rank.rank_emoji}")
            print(f"  Points: {user_rank.total_points}")
            print(f"  Rank level: {user_rank.rank_level}")
        else:
            print(f"  Could not get/create rank for test user {test_user_id}")
            
        return True
        
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("TESTING RANK LADDER FUNCTIONALITY")
    print("=" * 50)
    print()
    
    # Check database existence
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file does not exist: {DB_PATH}")
        return
    
    print(f"✅ Database found: {DB_PATH}")
    print()
    
    # Check rank definitions
    check_rank_definitions()
    
    # Test ranking integration
    integration_ok = check_ranking_integration()
    print()
    
    # Test rank ladder display
    if integration_ok:
        display_ok = test_rank_ladder_display()
        print()
        
        if display_ok:
            print("✅ Rank ladder functionality appears to be working!")
        else:
            print("❌ Rank ladder display has issues")
    else:
        print("❌ Cannot test rank ladder display due to ranking integration issues")

if __name__ == "__main__":
    main()
