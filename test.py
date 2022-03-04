member_predictions = {
"member1": 1980.0,
"member2": 2350.0,
"member3": 1800.0
}

real_price = 1900
# key, value = max(member_predictions.items(), key=lambda kv: (kv[1] <= real_price))


# print(key, value)


from functools import reduce

def find_max_with_limit(members, limit=None):

    member_tuples = members.items()
    if limit:
        member_tuples = list(filter(lambda x: x[1] <= limit, member_tuples))
        if len(member_tuples) > 0:
            return reduce(lambda x, y: x if x[1] > y[1] else y, member_tuples)


print(find_max_with_limit(member_predictions, limit=2200))