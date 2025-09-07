#!/usr/bin/env python3
"""
Test script to verify the point system behavior for confession submission, approval, and rejection
"""

import sys
sys.path.insert(0, '.')

from enhanced_ranking_system import EnhancedPointSystem

def test_point_system():
    """Test the enhanced point system"""
    point_system = EnhancedPointSystem()
    
    print("=== Point System Test ===")
    print()
    
    # Test confession submission (should be 0 points now)
    submission_points = point_system.calculate_points('confession_submitted')
    print(f"Confession submission points: {submission_points}")
    
    # Test confession approval (should be 50 points)
    approval_points = point_system.calculate_points('confession_approved')
    print(f"Confession approval points: {approval_points}")
    
    # Test confession rejection (should be -3 points)
    rejection_points = point_system.calculate_points('content_rejected')
    print(f"Confession rejection penalty: {rejection_points}")
    
    print()
    print("=== Test Results ===")
    
    # Verify expected behavior
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Submission should give 0 points
    if submission_points == 0:
        print("✅ Test 1 PASSED: Confession submission awards 0 points")
        tests_passed += 1
    else:
        print(f"❌ Test 1 FAILED: Expected 0 points for submission, got {submission_points}")
    
    # Test 2: Approval should give 50 points
    if approval_points == 50:
        print("✅ Test 2 PASSED: Confession approval awards 50 points")
        tests_passed += 1
    else:
        print(f"❌ Test 2 FAILED: Expected 50 points for approval, got {approval_points}")
    
    # Test 3: Rejection should give -3 points
    if rejection_points == -3:
        print("✅ Test 3 PASSED: Confession rejection penalty is -3 points")
        tests_passed += 1
    else:
        print(f"❌ Test 3 FAILED: Expected -3 points for rejection, got {rejection_points}")
    
    print()
    print(f"Overall: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Point system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the point system configuration.")
        return False

if __name__ == "__main__":
    test_point_system()
