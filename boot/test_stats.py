from stats import get_user_stats

user_id = 1298849354
print(f'Testing with user_id: {user_id}')

result = get_user_stats(user_id)
print(f'Stats result: {result}')

if not result:
    print('No statistics available. Submit your first confession!')
else:
    print('Stats found successfully!')
    print(f'Total confessions: {result["total_confessions"]}')
    print(f'Approved confessions: {result["approved_confessions"]}')
