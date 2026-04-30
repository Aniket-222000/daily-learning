import requests
import random
import os
from datetime import date

# ─────────────────────────────────────────────
# A curated list of real TIL topics.
# The script picks one randomly each day.
# You can add your own entries to this list!
# ─────────────────────────────────────────────
TOPICS = [
    {
        "title": "Python generators vs iterators",
        "content": """Generators are a simple way to create iterators using `yield`.
Unlike a regular function that returns once, a generator pauses at each `yield`
and resumes where it left off. This makes them memory-efficient for large data.

```python
def count_up(n):
    for i in range(n):
        yield i   # pauses here each time

for num in count_up(1000000):
    print(num)   # only one number in memory at a time
```

**Key difference:** An iterator requires `__iter__` and `__next__` methods.
A generator creates both automatically via `yield`.
"""
    },
    {
        "title": "What is a database index and why does it matter?",
        "content": """An index is a separate data structure (usually a B-tree) that the database
maintains alongside your table to speed up lookups.

Without an index, a query like `WHERE email = 'a@b.com'` scans every row.
With an index on `email`, the database jumps directly to the matching rows.

**Trade-off:** Indexes speed up reads but slow down writes (inserts/updates),
because the index must also be updated. Only index columns you frequently query.

```sql
CREATE INDEX idx_users_email ON users(email);
```
"""
    },
    {
        "title": "The difference between == and is in Python",
        "content": """`==` checks value equality. `is` checks identity (same object in memory).

```python
a = [1, 2, 3]
b = [1, 2, 3]

print(a == b)   # True  — same values
print(a is b)   # False — different objects in memory

c = a
print(a is c)   # True  — same object
```

Always use `==` for value comparisons. Use `is` only when checking
for `None` (e.g., `if x is None:`), which is the Python convention.
"""
    },
    {
        "title": "HTTP status codes every developer should know",
        "content": """| Code | Meaning |
|------|---------|
| 200  | OK — request succeeded |
| 201  | Created — resource was created |
| 204  | No Content — success, nothing to return |
| 301  | Moved Permanently — redirect forever |
| 400  | Bad Request — client sent invalid data |
| 401  | Unauthorized — not logged in |
| 403  | Forbidden — logged in but no permission |
| 404  | Not Found |
| 429  | Too Many Requests — rate limited |
| 500  | Internal Server Error — server crashed |
| 503  | Service Unavailable — server overloaded |

**Tip:** 4xx = client's fault. 5xx = server's fault.
"""
    },
    {
        "title": "Git rebase vs merge — when to use which",
        "content": """Both integrate changes from one branch into another, but differently.

**Merge** preserves history with a merge commit:
```
main:    A---B---C---M
feature:         D---E--/
```

**Rebase** replays your commits on top of the target, creating a linear history:
```
main:    A---B---C---D'---E'
```

**Rule of thumb:**
- Use `merge` for integrating finished feature branches into `main`
- Use `rebase` to update your local feature branch with latest `main` changes
- Never rebase commits that have been pushed to a shared branch
"""
    },
    {
        "title": "Big O notation — a quick reference",
        "content": """Big O describes how an algorithm's time/space scales with input size `n`.

| Notation   | Name        | Example                        |
|------------|-------------|--------------------------------|
| O(1)       | Constant    | Dictionary lookup              |
| O(log n)   | Logarithmic | Binary search                  |
| O(n)       | Linear      | Loop through a list            |
| O(n log n) | Linearithmic| Merge sort, Heap sort          |
| O(n²)      | Quadratic   | Nested loops (bubble sort)     |
| O(2ⁿ)      | Exponential | Recursive Fibonacci (naive)    |

**Tip:** When you see a nested loop over the same collection, that's usually O(n²).
"""
    },
    {
        "title": "CSS Flexbox vs Grid — when to use which",
        "content": """**Flexbox** is one-dimensional — it lays items out in a row OR a column.
Best for: navigation bars, centering a single item, distributing items in a line.

```css
.container { display: flex; justify-content: space-between; align-items: center; }
```

**Grid** is two-dimensional — rows AND columns at the same time.
Best for: page layouts, card grids, anything with rows and columns.

```css
.container { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
```

**Rule of thumb:** Component layout → Flexbox. Page layout → Grid.
"""
    },
    {
        "title": "What is a REST API?",
        "content": """REST (Representational State Transfer) is a set of conventions for building web APIs.

**Core idea:** Every resource (user, post, product) has a URL, and you interact
with it using standard HTTP methods:

| Method | Action         | Example              |
|--------|----------------|----------------------|
| GET    | Read           | GET /users/42        |
| POST   | Create         | POST /users          |
| PUT    | Replace        | PUT /users/42        |
| PATCH  | Partial update | PATCH /users/42      |
| DELETE | Delete         | DELETE /users/42     |

**Key principle:** REST is stateless — each request contains all the info
the server needs. No session stored on the server between requests.
"""
    },
    {
        "title": "How DNS works",
        "content": """When you type `google.com` in your browser, here's what happens:

1. Your OS checks its local DNS cache
2. If not cached, asks your ISP's DNS resolver
3. The resolver asks a Root nameserver → gets told where `.com` records live
4. Asks the `.com` TLD nameserver → gets told where `google.com` records live
5. Asks Google's authoritative nameserver → gets the IP address
6. Your browser connects to that IP

The whole process takes milliseconds and is cached at each step to avoid
repeating it. TTL (Time To Live) controls how long each answer is cached.
"""
    },
    {
        "title": "Mutable vs immutable data in Python",
        "content": """**Mutable** objects can be changed after creation. **Immutable** cannot.

| Mutable       | Immutable          |
|---------------|--------------------|
| list          | int, float, bool   |
| dict          | str                |
| set           | tuple              |
| bytearray     | frozenset          |

```python
# Strings are immutable — you always get a new object
s = "hello"
s.upper()   # does NOT change s
s = s.upper()   # reassign to get the new value

# Lists are mutable — operations change the same object
lst = [1, 2, 3]
lst.append(4)   # modifies lst in place
```

**Why it matters:** Immutable objects are safe as dictionary keys and in sets.
Mutable objects passed to functions can be changed inside the function.
"""
    },
    {
        "title": "Understanding async/await in JavaScript",
        "content": """`async/await` is syntactic sugar over Promises, making async code read like sync code.

```javascript
// Old way with .then()
fetch('/api/user')
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));

// Modern way with async/await
async function getUser() {
  try {
    const res = await fetch('/api/user');
    const data = await res.json();
    console.log(data);
  } catch (err) {
    console.error(err);
  }
}
```

**Key rule:** `await` can only be used inside an `async` function.
Under the hood, it's still Promises — `async/await` just makes it easier to read.
"""
    },
    {
        "title": "SQL JOINs explained simply",
        "content": """JOINs combine rows from two tables based on a related column.

```
users:  id | name       orders: id | user_id | item
        1  | Aarav              1  |    1    | Book
        2  | Priya              2  |    1    | Pen
        3  | Ravi               3  |    2    | Bag
```

| JOIN type    | Returns                                        |
|--------------|------------------------------------------------|
| INNER JOIN   | Only rows with a match in BOTH tables          |
| LEFT JOIN    | All rows from left table + matches from right  |
| RIGHT JOIN   | All rows from right table + matches from left  |
| FULL JOIN    | All rows from both tables                      |

```sql
-- Get all users and their orders (users with no orders included)
SELECT users.name, orders.item
FROM users
LEFT JOIN orders ON users.id = orders.user_id;
```
"""
    },
]


def get_topic_for_today():
    """Pick a topic based on day of year so it's consistent if re-run same day."""
    day_of_year = date.today().timetuple().tm_yday
    return TOPICS[day_of_year % len(TOPICS)]


def write_til_file(topic):
    today = date.today().isoformat()   # e.g. 2025-04-28
    folder = "entries"
    os.makedirs(folder, exist_ok=True)
    filepath = f"{folder}/{today}.md"

    content = f"""# TIL: {topic['title']}

*{today}*

---

{topic['content'].strip()}

---

*Auto-generated as part of my daily learning log.*
"""

    with open(filepath, "w") as f:
        f.write(content)

    print(f"✅ Written: {filepath}")
    return filepath


def update_readme():
    """Keep a running index in README.md"""
    folder = "entries"
    entries = sorted(os.listdir(folder), reverse=True) if os.path.exists(folder) else []

    lines = [
        "# 📚 Daily TIL — Today I Learned\n",
        "A daily log of programming concepts, tips, and discoveries.\n",
        "Updated automatically every day via GitHub Actions.\n\n",
        "## Recent entries\n\n",
    ]

    for filename in entries[:30]:   # show latest 30
        date_str = filename.replace(".md", "")
        lines.append(f"- [{date_str}](entries/{filename})\n")

    lines.append(f"\n---\n*{len(entries)} entries total.*\n")

    with open("README.md", "w") as f:
        f.writelines(lines)

    print("✅ README.md updated")


if __name__ == "__main__":
    topic = get_topic_for_today()
    write_til_file(topic)
    update_readme()
