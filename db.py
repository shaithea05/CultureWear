# Simulated in-memory DB for demo purposes

USERS: dict[str, dict] = {}          # email -> user
SESSIONS: dict[str, str] = {}        # token -> email
REWARDS: dict[str, int] = {}         # email -> points

WELCOME_BONUS = 500

NFTS: dict[str, dict] = {}           # token_id -> {wear_level, cleans_30d, late_deliveries, returns, events[]}

BONDS: dict[str, dict] = {}          # bond_id -> {...}
RENTAL_HISTORY: list[dict] = []      # audit log