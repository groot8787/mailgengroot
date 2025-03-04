import logging
import re
import random
import string
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# File to store all generated emails
GENERATED_EMAILS_FILE = "generated_emails.txt"

# File to store user activity
USER_ACTIVITY_FILE = "user_activity.txt"

# List of admin user IDs (replace with your Telegram user IDs)
ADMIN_USER_IDS = [5053822685, 6751603241] # Add more IDs as needed

# Lists of common first names and last names to make emails look realistic
FIRST_NAMES = [
    "alice", "bob", "charlie", "david", "emma", "akash", "george", "hannah", "ian", "julia",
    "liam", "olivia", "noah", "ava", "william", "sophia", "james", "isabella", "oliver", "mia",
    "benjamin", "amelia", "elijah", "harper", "lucas", "evelyn", "mason", "abigail", "logan", "emily",
    "alexander", "charlotte", "ethan", "madison", "jacob", "elizabeth", "michael", "avery", "daniel", "sofia",
    "henry", "ella", "jackson", "scarlett", "sebastian", "grace", "aiden", "chloe", "matthew", "victoria",
    "samuel", "ria", "david", "layla", "joseph", "penelope", "carter", "luna", "owen", "zoey",
    "wyatt", "sarah", "john", "lily", "dylan", "hannah", "luke", "aria", "gabriel", "aubrey",
    "anthony", "ellie", "isaac", "stella", "grayson", "nora", "jaxon", "zoe", "levi", "leah",
    "julian", "hazel", "christopher", "violet", "joshua", "aurora", "andrew", "savannah", "theodore", "audrey",
    "caleb", "brooklyn", "ryan", "bella", "asher", "claire", "nathan", "skylar", "thomas", "lucy",
    "leo", "paisley", "elias", "everly", "charles", "anna", "hudson", "caroline", "eli", "nova",
    "aaron", "genesis", "robert", "emilia", "tyler", "kennedy", "adrian", "samantha", "james", "maya",
    "josiah", "willow", "christian", "kylie", "landon", "eleanor", "colton", "delilah", "roman", "isla",
    "axel", "riley", "brooks", "kinsley", "jonathan", "naomi", "easton", "valentina", "mateo", "maya",
    "jace", "ivy", "maxwell", "serenity", "miles", "liliana", "sawyer", "gianna", "jason", "clara",
    "kaiden", "vivian", "emmett", "alina", "jayden", "elena", "luca", "alice", "nathaniel", "laila",
    "anthony", "lila", "isaiah", "adeline", "chase", "arabella", "adam", "jasmine", "nolan", "elise",
    "riley", "remi", "brayden", "mackenzie", "nicholas", "adele", "evan", "amara", "colin", "kayla",
    "xavier", "lucia", "cameron", "khloe", "kayden", "isabelle", "cooper", "mariah", "parker", "jade",
    "maddox", "alaina", "ashton", "alexa", "bentley", "juliana", "kingston", "melanie", "dominick", "rachel",
    "tristan", "brooklynn", "joshua", "sienna", "jose", "paige", "bryson", "jocelyn", "jordan", "daisy",
    "micah", "mila", "colt", "reagan", "axel", "harmony", "griffin", "alyssa", "dean", "fiona",
    "austin", "alexis", "max", "juliette", "oscar", "londyn", "diego", "kendall", "jonah", "katherine",
    "elliott", "jordyn", "bennett", "sadie", "king", "trinity", "lincoln", "lila", "zachary", "lola",
    "calvin", "emery", "braxton", "morgan", "jaxson", "savannah", "jaden", "leilani", "ryder", "madelyn",
    "myles", "reese", "hayden", "miranda", "carson", "kaylee", "blake", "kylie", "nathan", "julianna",
    "tucker", "alana", "silas", "angelina", "weston", "makayla", "ezra", "isabel", "damian", "marley",
    "gavin", "alivia", "karter", "mckenzie", "kingston", "cora", "zion", "brianna", "cole", "kelsey",
    "xander", "payton", "barrett", "allyson", "jude", "sierra", "paul", "alexandra", "joel", "jane",
    "preston", "elaina", "oscar", "lilith", "kaleb", "kaitlyn", "maximus", "margaret", "remington", "catherine",
    "dallas", "julie", "corey", "kendal", "holden", "kylee", "bryce", "kyla", "omar", "katie",
    "arjun", "anika", "kunal", "anjali", "rahul", "divya", "vivek", "kavya", "suresh", "meera",
    "rajesh", "priya", "manoj", "neha", "vikram", "shreya", "anil", "pooja", "sanjay", "ritu",
    "deepak", "sonia", "mohit", "swati", "rohit", "tanvi", "naveen", "kriti", "prakash", "isha",
    "sachin", "nidhi", "ajay", "shilpa", "vijay", "monika", "ravi", "pallavi", "amit", "sneha",
    "nitin", "anjali", "prashant", "kiran", "sandeep", "rekha", "sunil", "manisha", "rajeev", "aarti",
    "anand", "deepa", "ashok", "shweta", "gaurav", "komal", "varun", "radha", "abhishek", "sakshi",
    "dinesh", "preeti", "mukesh", "jyoti", "shyam", "varsha", "ramesh", "usha", "harish", "nisha",
    "mahesh", "lata", "suresh", "geeta", "kishore", "sarita", "pankaj", "mamta", "raj", "kavita",
    "vinod", "sunita", "sanjeev", "rani", "ajit", "pooja", "manish", "shalini", "subhash", "anita",
    "yogesh", "kirti", "rakesh", "sapna", "bharat", "kajal", "dilip", "manju", "sanjay", "rekha",
    "narendra", "sushma", "ram", "meenakshi", "kunal", "arti", "anup", "kiran", "rajiv", "shobha",
    "pradeep", "smita", "sushil", "puja", "ashish", "neetu", "amitabh", "shivani", "rajendra", "kavita",
    "sanjay", "anju", "rajkumar", "poonam", "vishal", "sadhana", "arun", "jyotsna", "mohan", "kavita",
    "suresh", "shubha", "pramod", "sarita", "rajesh", "kavita", "anil", "kavita", "sanjay", "kavita",
    "rajesh", "kavita", "anil", "kavita", "sanjay", "kavita", "rajesh", "kavita", "anil", "kavita"
]

LAST_NAMES = [
    "smith", "johnson", "williams", "brown", "jones", "garcia", "miller", "davis", "rodriguez", "martinez",
    "hernandez", "lopez", "gonzalez", "wilson", "anderson", "thomas", "taylor", "moore", "jackson", "martin",
    "lee", "perez", "thompson", "white", "harris", "sanchez", "clark", "ramirez", "lewis", "robinson",
    "walker", "young", "allen", "king", "wright", "scott", "torres", "nguyen", "hill", "flores",
    "green", "adams", "nelson", "baker", "hall", "rivera", "campbell", "mitchell", "carter", "roberts",
    "gomez", "phillips", "evans", "turner", "diaz", "parker", "cruz", "edwards", "collins", "reyes",
    "stewart", "morris", "morales", "murphy", "cook", "rogers", "gutierrez", "ortiz", "morgan", "cooper",
    "peterson", "bailey", "reed", "kelly", "howard", "ramos", "kim", "cox", "ward", "richardson",
    "watson", "brooks", "chavez", "wood", "james", "bennet", "gray", "mendoza", "ruiz", "hughes",
    "price", "alvarez", "castillo", "sanders", "patel", "myers", "long", "ross", "foster", "jimenez",
    "powell", "jenkins", "perry", "russell", "sullivan", "bell", "coleman", "butler", "henderson", "barnes",
    "gonzales", "fisher", "vasquez", "simmons", "romero", "jordan", "patterson", "alexander", "hamilton", "graham",
    "reynolds", "griffin", "wallace", "moreno", "west", "cole", "hayes", "bryant", "herrera", "gibson",
    "ellis", "tran", "medina", "aguilar", "stevens", "murray", "ford", "castro", "marshall", "owens",
    "harrison", "fernandez", "mcdonald", "woods", "washington", "kennedy", "wells", "vargas", "henry", "chen",
    "freeman", "webb", "tucker", "guzman", "burns", "crawford", "olson", "simpson", "porter", "hunter",
    "gordon", "mendez", "silva", "shaw", "snyder", "mason", "dixon", "munoz", "hunt", "hicks",
    "holmes", "palmer", "wagner", "black", "robertson", "boyd", "rose", "stone", "salazar", "fox",
    "warren", "mills", "meyer", "rice", "schmidt", "garza", "daniels", "ferguson", "nichols", "stephens",
    "soto", "weaver", "ryan", "gardner", "payne", "grant", "dunn", "kelley", "spencer", "hawkins",
    "arnold", "pierce", "vazquez", "hansen", "peters", "santos", "hart", "bradley", "knight", "elliott",
    "cunningham", "duncan", "armstrong", "hudson", "carroll", "lane", "riley", "andrews", "alvarado", "ray",
    "delgado", "berry", "perkins", "hoffman", "johnston", "matthews", "pena", "richards", "contreras", "willis",
    "carpenter", "lawrence", "sandoval", "guerrero", "george", "chapman", "rios", "estrada", "ortega", "watkins",
    "greene", "nunez", "wheeler", "valdez", "harper", "burke", "larson", "santiago", "maldonado", "morrison",
    "franklin", "carlson", "austin", "dominguez", "todd", "stanley", "curry", "schultz", "walters", "fields",
    "mack", "lamb", "craig", "chambers", "maxwell", "barker", "logan", "conner", "holloway", "summers",
    "bush", "wilkins", "glover", "patterson", "leonard", "blake", "manning", "cohen", "harmon", "rodgers",
    "robbins", "newton", "todd", "blair", "higgins", "ingram", "reese", "cannon", "strickland", "townsend",
    "potter", "goodwin", "walton", "rowe", "hampton", "ortega", "patton", "swanson", "joseph", "francis",
    "goodman", "maldonado", "yates", "becker", "erickson", "hodges", "rios", "conner", "adkins", "webster",
    "norman", "malone", "hammond", "flowers", "cobb", "moody", "quinn", "blake", "maxwell", "pope",
    "floyd", "osborne", "paul", "mccarthy", "guerrero", "lindsey", "estrada", "sandoval", "gibbs", "tyler",
    "gross", "fitzgerald", "stokes", "doyle", "sherman", "saunders", "wise", "colon", "gill", "farmer",
    "hines", "gallagher", "durham", "hubbard", "cannon", "miranda", "wang", "saunders", "tate", "mack",
    "sharp", "bowman", "lowe", "leon", "jacobs", "chandra", "gupta", "sharma", "patel", "kumar",
    "singh", "verma", "tiwari", "yadav", "shah", "jain", "mehta", "bhatt", "srivastava", "das",
    "rao", "naik", "pandey", "thakur", "choudhary", "reddy", "agarwal", "kapoor", "malhotra", "trivedi",
    "saxena", "mishra", "desai", "joshi", "sinha", "nair", "rajan", "menon", "iyer", "pillai",
    "chopra", "ravi", "khan", "pathak", "gandhi", "dubey", "ram", "bose", "banerjee", "mukherjee",
    "chakraborty", "dutta", "sen", "basu", "ghosh", "nayak", "pal", "bajaj", "sarin", "kapoor",
    "talwar", "bansal", "goel", "arora", "seth", "tandon", "mathur", "goyal", "khanna", "bhalla",
    "malik", "dua", "saini", "chauhan", "rana", "rajput", "solanki", "parmar", "thakkar", "panchal",
    "meena", "khatri", "aggarwal", "lad", "bhardwaj", "bakshi", "deol", "dhawan", "grewal", "sodhi",
    "singhal", "wadhwa", "khurana", "sehgal", "bhasin", "sur", "kohli", "narang", "suri", "batra",
    "kundra", "lal", "mahajan", "oberoi", "walia", "bindra", "chadha", "dhingra", "gambhir", "sawhney",
    "talwar", "bhatia", "chhabra", "dhaliwal", "garg", "kakar", "luthra", "mahindra", "nanda", "puri",
    "sahni", "sibal", "taneja", "vohra", "ahluwalia", "bir", "cheema", "dang", "gill", "handa",
    "johar", "kapur", "lamba", "makkar", "nagpal", "pannu", "sachdev", "tuli", "wahi", "zutshi"
]

# Function to validate the domain
def is_valid_domain(domain: str) -> bool:
    """Check if the domain is valid (basic validation)."""
    # Regex to check if the domain contains at least one dot and valid characters
    domain_pattern = re.compile(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return bool(domain_pattern.match(domain))

# Function to load previously generated emails from the file
def load_generated_emails() -> set:
    """Load all previously generated emails from the file."""
    try:
        with open(GENERATED_EMAILS_FILE, "r") as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

# Function to save a new email to the file
def save_generated_email(email: str) -> None:
    """Save a new email to the file."""
    with open(GENERATED_EMAILS_FILE, "a") as file:
        file.write(email + "\n")

# Function to track user activity
def track_user_activity(user_id: int, username: str) -> None:
    """Track user activity by saving user ID and username to a file."""
    try:
        with open(USER_ACTIVITY_FILE, "a") as file:
            file.write(f"{user_id},{username}\n")
    except Exception as e:
        logger.error(f"Error tracking user activity: {e}")

# Function to get unique users and their details
def get_unique_users() -> tuple[int, list[tuple[int, str]]]:
    """Get the number of unique users and their details (user ID and username)."""
    try:
        with open(USER_ACTIVITY_FILE, "r") as file:
            lines = file.read().splitlines()
            unique_users = set(lines)  # Use a set to remove duplicates
            user_details = [tuple(line.split(",")) for line in unique_users]  # Convert to (user_id, username) tuples
            return len(unique_users), user_details
    except FileNotFoundError:
        return 0, []

# Function to generate a realistic-looking email address with a fixed length of 12 and a 3-digit number
def generate_realistic_email(domain: str, generated_emails: set) -> str:
    """Generate a realistic-looking email address with a fixed length of 12 and a 3-digit number."""
    while True:
        # Randomly select a first name and last name
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        # Combine first name and last name
        base_username = f"{first_name}{last_name}"

        # Trim or pad the base username to ensure the total length is 9 (12 - 3 for the random digits)
        if len(base_username) > 9:
            base_username = base_username[:9]  # Trim to 9 characters
        else:
            base_username = base_username.ljust(9, random.choice(string.ascii_lowercase))  # Pad with random lowercase letters

        # Add a random 3-digit number at the end
        random_digits = str(random.randint(100, 999))  # Random 3-digit number
        username = f"{base_username}{random_digits}"  # Combine to make 12 characters

        # Combine username and domain to form email
        email = f"{username}@{domain}"

        # Check if the email is already generated
        if email not in generated_emails:
            generated_emails.add(email)  # Add to the set of generated emails
            save_generated_email(email)  # Save the email to the file
            return email

# Command handler for the /start command
async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    track_user_activity(user.id, user.username)  # Track user activity
    await update.message.reply_text(
        "Welcome! Use the command `.gen domain.com 10` to generate 10 realistic-looking email addresses for domain.com."
    )

# Message handler to process the .gen command
async def handle_gen_command(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    track_user_activity(user.id, user.username)  # Track user activity

    user_input = update.message.text.strip()

    # Check if the input starts with .gen
    if user_input.startswith(".gen"):
        parts = user_input.split()

        # Validate input
        if len(parts) < 2:
            await update.message.reply_text("Please provide a domain name and optionally the number of emails to generate.")
            return

        domain = parts[1]
        quantity = 1  # Default to 1 email if no quantity is specified

        # Check if the user provided a quantity
        if len(parts) > 2:
            try:
                quantity = int(parts[2])
                if quantity < 1 or quantity > 20:  # Limit to 20 emails max
                    await update.message.reply_text("Please specify a quantity between 1 and 20.")
                    return
            except ValueError:
                await update.message.reply_text("Invalid quantity. Please provide a number.")
                return

        # Validate the domain
        if not is_valid_domain(domain):
            await update.message.reply_text("Invalid domain. Please provide a valid domain name (e.g., example.com).")
            return

        # Load previously generated emails
        generated_emails = load_generated_emails()

        # Generate the emails
        emails = []
        for _ in range(quantity):
            email = generate_realistic_email(domain, generated_emails)
            emails.append(email)

        # Format the response in mono format (using Markdown backticks)
        response = (
            "Here's your generated mail\n\n"
            f"Domain Name - `{domain}`\n"
            "-----------------------------------\n"
            + "\n".join([f"`{email}`" for email in emails]) +
            "\n-----------------------------------\n"
            "Your Generated Mail"
        )

        # Send the response with Markdown parsing enabled
        await update.message.reply_text(response, parse_mode="Markdown")
    else:
        await update.message.reply_text("Invalid command. Use `.gen domain.com 10` to generate emails.")

# Command handler for the /stats command (admin-only)
async def stats(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    if user.id in ADMIN_USER_IDS:  # Check if the user is in the admin list
        unique_users_count, user_details = get_unique_users()
        if unique_users_count == 0:
            await update.message.reply_text("No users have interacted with the bot yet.")
        else:
            # Format the list of users
            user_list = "\n".join([f"User ID: `{user_id}`, Username: `{username}`" for user_id, username in user_details])
            response = (
                f"Total unique users: {unique_users_count}\n\n"
                "User Details:\n"
                f"{user_list}"
            )
            await update.message.reply_text(response, parse_mode="Markdown")
    else:
        await update.message.reply_text("You do not have permission to use this command.")

# Error handler
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

def main() -> None:
    # Get the bot token from the environment variable
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set.")
        return

    # Create the Application and pass it your bot's token
    application = Application.builder().token(bot_token).build()

    # Register command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))  # Add /stats command
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gen_command))

    # Register error handler
    application.add_error_handler(error)

    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()