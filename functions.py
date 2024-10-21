from databases import Database
async def check(d,database):
    user_ids = await database.fetch_all(query="SELECT id from users;")
    print(user_ids,type(user_ids))
    if not user_ids:
        return False
    else:
        user_ids = [dict(i)["id"] for i in user_ids]
        print(user_ids)
    count = 0
    for key in d:
        try:
            a = int(key)
            if a not in user_ids:
                return False
        except:
            return False
        count += d[key]

    if count != 100:
        return False   

    return True
