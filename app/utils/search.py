def naive_string_match(T, P, idx=-1):
    n = len(T)
    m = len(P)

    for s in range(0, n - m + 1):
        k = 0
        for i in range(0, m):
            if T[s + i] != P[i] and idx != i:
                break
            else:
                k += 1
        if k == m:
            return s
    return -1


def best_match(w1, w2):
    if naive_string_match(w1, w2) >= 0:
        return 1
    for i in range(1, len(w2) - 1):
        if naive_string_match(w1, w2, i) >= 0:
            return 0
    return -1


print(best_match("apple.com", "apple"))
r = ()
print(r[0])
