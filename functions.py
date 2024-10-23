from databases import Database


async def data_validation(amount, method, d, all_users):
    if method == "equal":
        if d != None:
            return False
        else:
            return True
    else:
        count = 0
        for key in d:
            try:
                a = int(key)
                if a not in all_users:
                    return False
            except:
                return False
            count += d[key]
        if method == "exact":
            if amount != count:
                return False
        else:
            if count != 100:
                return False

        return True
