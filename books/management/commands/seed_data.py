"""
Management command: python manage.py seed_data

Populates the database with realistic sample data:
  - 6 categories
  - 10 authors
  - 30 books
  - 6 student users
  - borrow records (active + returned)
  - reviews / ratings
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from books.models import Author, Category, Book
from borrowing.models import BorrowRecord
from reviews.models import Review
from accounts.models import StudentProfile


# ── Raw data ──────────────────────────────────────────────────────────────────

CATEGORIES = [
    ("Fiction",          "Novels, short stories, and other imaginative literature."),
    ("Science",          "Books covering physics, biology, chemistry, and scientific discovery."),
    ("History",          "Explorations of world history, civilisations, and historical events."),
    ("Technology",       "Programming, computing, engineering, and digital innovation."),
    ("Philosophy",       "Works on ethics, metaphysics, logic, and great philosophical thinkers."),
    ("Self-Development", "Personal growth, productivity, leadership, and well-being."),
]

AUTHORS = [
    ("George Orwell",      "Eric Arthur Blair, known by his pen name George Orwell, was an English novelist, essayist, journalist, and critic known for his lucid prose, social criticism, and opposition to totalitarianism."),
    ("J.K. Rowling",       "British author best known for the Harry Potter fantasy series, which has won multiple awards and sold more than 500 million copies worldwide."),
    ("Yuval Noah Harari",  "Israeli public intellectual, historian, and professor, known for the popular science bestsellers Sapiens, Homo Deus, and 21 Lessons for the 21st Century."),
    ("Stephen Hawking",    "Theoretical physicist, cosmologist, and author who was director of research at the Centre for Theoretical Cosmology at Cambridge. Author of A Brief History of Time."),
    ("Marcus Aurelius",    "Roman Emperor from 161 to 180 AD and a Stoic philosopher. His Meditations is a series of personal writings on Stoic philosophy."),
    ("Cal Newport",        "American non-fiction author and associate professor of computer science at Georgetown University, known for books on productivity and deep work."),
    ("Frank Herbert",      "American science fiction author best known for the novel Dune and its sequels, one of the best-selling science fiction novels of all time."),
    ("Agatha Christie",    "English writer known for her 66 detective novels and 14 short story collections, particularly those revolving around Hercule Poirot and Miss Marple."),
    ("Malcolm Gladwell",   "Canadian journalist, author, and public speaker known for his thought-provoking analysis of research in the social sciences and popular culture."),
    ("James Clear",        "American author, entrepreneur, and photographer known for his New York Times bestselling book Atomic Habits."),
]

BOOKS = [
    # title, author_idx, category_idx, isbn, pages, language, total_copies, published, description
    ("1984",                              0, 0, "9780451524935", 328,  "English", 5, "1949-06-08",
     "A dystopian novel set in a totalitarian society ruled by Big Brother, exploring surveillance, propaganda, and the erosion of truth."),

    ("Animal Farm",                       0, 0, "9780451526342", 140,  "English", 4, "1945-08-17",
     "An allegorical novella reflecting events leading up to the Russian Revolution and the Stalinist era of the Soviet Union."),

    ("Harry Potter and the Philosopher's Stone", 1, 0, "9780747532743", 223, "English", 6, "1997-06-26",
     "The first book in the beloved Harry Potter series, introducing a young wizard's journey to Hogwarts School of Witchcraft and Wizardry."),

    ("Harry Potter and the Chamber of Secrets",  1, 0, "9780747538493", 251, "English", 4, "1998-07-02",
     "Harry Potter's second year at Hogwarts, uncovering the mystery of the Chamber of Secrets and the Heir of Slytherin."),

    ("Sapiens: A Brief History of Humankind",    2, 2, "9780062316097", 443, "English", 5, "2011-01-01",
     "A sweeping narrative of humanity's history and impact on the world, from the Stone Age to the 21st century."),

    ("Homo Deus: A Brief History of Tomorrow",   2, 2, "9780062464316", 450, "English", 3, "2015-09-04",
     "An exploration of the future of humanity, examining data religion, artificial intelligence, and the obsolescence of human agency."),

    ("A Brief History of Time",                  3, 1, "9780553380163", 212, "English", 4, "1988-04-01",
     "A landmark volume in science writing that takes the reader on a journey through space, time, black holes, and the Big Bang."),

    ("The Universe in a Nutshell",               3, 1, "9780553802023", 224, "English", 3, "2001-11-06",
     "Stephen Hawking's follow-up to A Brief History of Time, exploring M-theory, imaginary time, and the nature of the universe."),

    ("Meditations",                              4, 4, "9780812968255", 254, "English", 5, "0180-01-01",
     "Personal writings of the Roman Emperor Marcus Aurelius, recording his private notes to himself and his ideas on Stoic philosophy."),

    ("Deep Work",                                5, 5, "9781455586691", 296, "English", 4, "2016-01-05",
     "Rules for focused success in a distracted world — Cal Newport argues that the ability to perform deep work is becoming increasingly rare and valuable."),

    ("Digital Minimalism",                       5, 5, "9780525536512", 284, "English", 3, "2019-02-05",
     "A philosophy of technology use in which you focus your online time on a small number of carefully selected activities."),

    ("Dune",                                     6, 0, "9780441013593", 688, "English", 5, "1965-08-01",
     "Set in the distant future amidst a feudal interstellar society, Dune follows young Paul Atreides as his family takes control of the desert planet Arrakis."),

    ("Dune Messiah",                             6, 0, "9780441172696", 256, "English", 3, "1969-01-01",
     "The second installment of the Dune Chronicles, continuing the story of Paul Atreides twelve years after his rise to power."),

    ("Murder on the Orient Express",             7, 0, "9780007119318", 256, "English", 5, "1934-01-01",
     "Hercule Poirot investigates a murder aboard the famous Orient Express train — a masterpiece of the golden age of detective fiction."),

    ("And Then There Were None",                 7, 0, "9780312330873", 272, "English", 4, "1939-11-06",
     "Ten strangers are lured to an isolated island and begin to be murdered one by one, in this best-selling mystery novel of all time."),

    ("The Tipping Point",                        8, 5, "9780316346627", 301, "English", 4, "2000-03-01",
     "How little things can make a big difference — Malcolm Gladwell examines the social epidemics that spread like viruses."),

    ("Outliers: The Story of Success",           8, 5, "9780316017930", 309, "English", 3, "2008-11-18",
     "Why do some people succeed far more than others? Gladwell examines the lives of outliers — Bill Gates, The Beatles, and others."),

    ("Blink",                                    8, 5, "9780316010665", 296, "English", 3, "2005-01-11",
     "The power of thinking without thinking — exploring the science of rapid cognition and the decisions we make in the blink of an eye."),

    ("Atomic Habits",                            9, 5, "9780735211292", 320, "English", 6, "2018-10-16",
     "An Easy and Proven Way to Build Good Habits and Break Bad Ones — the definitive guide to remarkable results through small changes."),

    ("The Origins of Virtue",                    2, 4, "9780670869329", 295, "English", 2, "1996-01-01",
     "Matt Ridley's exploration of the evolution of altruism and co-operation in human society, drawing on game theory and evolutionary biology."),

    ("Clean Code",                               5, 3, "9780132350884", 431, "English", 4, "2008-08-11",
     "A Handbook of Agile Software Craftsmanship — Robert C. Martin presents the best practices for writing clean, maintainable code."),

    ("The Pragmatic Programmer",                 5, 3, "9780135957059", 352, "English", 3, "2019-09-13",
     "From journeyman to master — a timeless guide to software development best practices and professional programming habits."),

    ("Design Patterns",                          5, 3, "9780201633610", 395, "English", 3, "1994-10-31",
     "Elements of Reusable Object-Oriented Software — the classic gang-of-four book defining 23 fundamental design patterns."),

    ("The Great Gatsby",                         0, 0, "9780743273565", 180, "English", 5, "1925-04-10",
     "A portrayal of the Jazz Age in all of its decadence and excess — Fitzgerald's story of wealth, love, and the American Dream."),

    ("Brave New World",                          0, 0, "9780060850524", 311, "English", 4, "1932-01-01",
     "Aldous Huxley's dystopian novel depicting a future society controlled by technology, conditioning, and the pursuit of pleasure."),

    ("The Republic",                             4, 4, "9780140455113", 416, "English", 3, "0380-01-01",
     "Plato's Socratic dialogue examining justice, the order of a just city-state, and the nature of the just man."),

    ("Thinking, Fast and Slow",                  8, 5, "9780374533557", 499, "English", 4, "2011-10-25",
     "Daniel Kahneman's exploration of two systems that drive the way we think — fast, intuitive thinking and slow, deliberate reasoning."),

    ("Brief Answers to the Big Questions",       3, 1, "9781473695993", 232, "English", 3, "2018-10-16",
     "Stephen Hawking's final book, tackling the most profound questions of our time — from the existence of God to the future of AI."),

    ("The Art of War",                           4, 4, "9781590302255", 273, "English", 4, "0500-01-01",
     "Sun Tzu's ancient Chinese military treatise — its influence extends beyond warfare to business strategy, sports, and philosophy."),

    ("Zero to One",                              9, 3, "9780804139021", 224, "English", 4, "2014-09-16",
     "Notes on startups, or how to build the future — Peter Thiel's contrarian thinking on innovation, monopolies, and creating something new."),
]

STUDENTS = [
    # username, first, last, email, password, phone
    ("alice_smith",   "Alice",   "Smith",   "alice@library.com",   "Pass@1234", "+1-202-555-0101"),
    ("bob_jones",     "Bob",     "Jones",   "bob@library.com",     "Pass@1234", "+1-202-555-0102"),
    ("carol_white",   "Carol",   "White",   "carol@library.com",   "Pass@1234", "+1-202-555-0103"),
    ("david_brown",   "David",   "Brown",   "david@library.com",   "Pass@1234", "+1-202-555-0104"),
    ("emma_davis",    "Emma",    "Davis",   "emma@library.com",    "Pass@1234", "+1-202-555-0105"),
    ("frank_miller",  "Frank",   "Miller",  "frank@library.com",   "Pass@1234", "+1-202-555-0106"),
]

# (username, book_title, status, days_ago_borrowed, days_ago_returned_or_none)
BORROWS = [
    ("alice_smith",  "1984",                                  "returned", 30, 16),
    ("alice_smith",  "Atomic Habits",                         "returned", 20, 5),
    ("alice_smith",  "Deep Work",                             "borrowed", 10, None),
    ("alice_smith",  "Sapiens: A Brief History of Humankind", "borrowed", 5,  None),

    ("bob_jones",    "Dune",                                  "returned", 45, 30),
    ("bob_jones",    "Harry Potter and the Philosopher's Stone", "returned", 25, 10),
    ("bob_jones",    "Murder on the Orient Express",          "borrowed", 8,  None),

    ("carol_white",  "A Brief History of Time",               "returned", 60, 45),
    ("carol_white",  "Meditations",                           "returned", 30, 15),
    ("carol_white",  "Thinking, Fast and Slow",               "borrowed", 12, None),
    ("carol_white",  "The Tipping Point",                     "borrowed", 3,  None),

    ("david_brown",  "Clean Code",                            "returned", 50, 36),
    ("david_brown",  "Design Patterns",                       "returned", 35, 21),
    ("david_brown",  "Zero to One",                           "borrowed", 7,  None),

    ("emma_davis",   "Animal Farm",                           "returned", 40, 26),
    ("emma_davis",   "Brave New World",                       "returned", 20, 6),
    ("emma_davis",   "Outliers: The Story of Success",        "borrowed", 6,  None),
    ("emma_davis",   "Blink",                                 "borrowed", 2,  None),

    ("frank_miller", "The Art of War",                        "returned", 55, 41),
    ("frank_miller", "Homo Deus: A Brief History of Tomorrow","returned", 28, 14),
    ("frank_miller", "The Great Gatsby",                      "borrowed", 13, None),  # overdue
]

# (username, book_title, rating, comment)
REVIEWS = [
    ("alice_smith",  "1984",                                  5, "A chilling masterpiece. Orwell's vision of a totalitarian future is as relevant today as ever. Absolutely essential reading."),
    ("alice_smith",  "Atomic Habits",                         5, "Life-changing! The idea of 1% improvements every day completely shifted my perspective on building habits. Highly recommend."),
    ("bob_jones",    "Dune",                                  5, "An epic saga that rewards patient reading. The world-building is unparalleled — a must-read for any science fiction fan."),
    ("bob_jones",    "Harry Potter and the Philosopher's Stone", 4, "A magical adventure that captures the imagination. The perfect start to one of the greatest series ever written."),
    ("carol_white",  "A Brief History of Time",               4, "Hawking explains incredibly complex concepts with remarkable clarity. An inspiring journey through cosmology."),
    ("carol_white",  "Meditations",                           5, "Marcus Aurelius speaks across two millennia. Simple, profound, and deeply practical Stoic wisdom for daily life."),
    ("david_brown",  "Clean Code",                            5, "Every software developer should read this. Martin's principles transformed the way I write and review code."),
    ("david_brown",  "Design Patterns",                       4, "Dense but invaluable. Understanding these patterns is a rite of passage for any serious software architect."),
    ("emma_davis",   "Animal Farm",                           5, "Deceptively simple yet devastatingly powerful. A perfect allegory that remains shockingly relevant in modern politics."),
    ("emma_davis",   "Brave New World",                       4, "Huxley's vision of a pleasure-controlled dystopia is more unsettling than Orwell's — and perhaps more prophetic."),
    ("frank_miller", "The Art of War",                        4, "Timeless strategic wisdom. Short chapters packed with insights applicable far beyond the battlefield."),
    ("frank_miller", "Homo Deus: A Brief History of Tomorrow", 3, "Thought-provoking but occasionally veers into speculation. Still a fascinating read about humanity's potential futures."),
]


class Command(BaseCommand):
    help = 'Seed the database with sample library data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush', action='store_true',
            help='Delete existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('  Flushing existing data...')
            Review.objects.all().delete()
            BorrowRecord.objects.all().delete()
            Book.objects.all().delete()
            Author.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.MIGRATE_HEADING('\nSeeding E-Library data...\n'))

        categories = self._seed_categories()
        authors    = self._seed_authors()
        books      = self._seed_books(authors, categories)
        users      = self._seed_users()
        self._seed_borrows(users, books)
        self._seed_reviews(users, books)

        self.stdout.write(self.style.SUCCESS('\nDone! Database seeded successfully.\n'))
        self.stdout.write(f'  Categories : {Category.objects.count()}')
        self.stdout.write(f'  Authors    : {Author.objects.count()}')
        self.stdout.write(f'  Books      : {Book.objects.count()}')
        self.stdout.write(f'  Students   : {User.objects.filter(is_staff=False).count()}')
        self.stdout.write(f'  Borrows    : {BorrowRecord.objects.count()}')
        self.stdout.write(f'  Reviews    : {Review.objects.count()}\n')

    # ── Seeders ───────────────────────────────────────────────────────────────

    def _seed_categories(self):
        self.stdout.write('  Creating categories...')
        result = {}
        for name, desc in CATEGORIES:
            obj, created = Category.objects.get_or_create(
                name=name, defaults={'description': desc}
            )
            result[name] = obj
            if created:
                self.stdout.write(f'    + {name}')
        return result

    def _seed_authors(self):
        self.stdout.write('  Creating authors...')
        result = {}
        for name, bio in AUTHORS:
            obj, created = Author.objects.get_or_create(
                name=name, defaults={'bio': bio}
            )
            result[name] = obj
            if created:
                self.stdout.write(f'    + {name}')
        return result

    def _seed_books(self, authors, categories):
        self.stdout.write('  Creating books...')
        result = {}
        cat_list = list(CATEGORIES)
        auth_list = list(AUTHORS)

        for (title, auth_idx, cat_idx, isbn, pages, lang,
             total, pub_str, desc) in BOOKS:

            author_name = auth_list[auth_idx][0]
            cat_name    = cat_list[cat_idx][0]

            # Parse published date (handle ancient dates like 0180)
            try:
                from datetime import date
                parts = pub_str.split('-')
                year  = int(parts[0])
                month = int(parts[1]) if len(parts) > 1 else 1
                day   = int(parts[2]) if len(parts) > 2 else 1
                # clamp to valid range
                if year < 1:
                    year = 1
                pub_date = date(year, month, day)
            except Exception:
                pub_date = None

            obj, created = Book.objects.get_or_create(
                title=title,
                defaults={
                    'author':           authors.get(author_name),
                    'category':         categories.get(cat_name),
                    'isbn':             isbn,
                    'pages':            pages,
                    'language':         lang,
                    'total_copies':     total,
                    'available_copies': total,
                    'published_date':   pub_date,
                    'description':      desc,
                }
            )
            result[title] = obj
            if created:
                self.stdout.write(f'    + {title}')
        return result

    def _seed_users(self):
        self.stdout.write('  Creating student users...')
        result = {}
        for username, first, last, email, password, phone in STUDENTS:
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                self.stdout.write(f'    ~ {username} (already exists)')
            else:
                user = User.objects.create_user(
                    username=username, first_name=first,
                    last_name=last, email=email, password=password,
                )
                self.stdout.write(f'    + {username}')

            # update phone on profile
            try:
                profile = user.profile
                if not profile.phone:
                    profile.phone = phone
                    profile.save()
            except Exception:
                StudentProfile.objects.get_or_create(user=user, defaults={'phone': phone})

            result[username] = user
        return result

    def _seed_borrows(self, users, books):
        self.stdout.write('  Creating borrow records...')
        today = timezone.now().date()

        for username, title, status, days_borrowed, days_returned in BORROWS:
            user = users.get(username)
            book = books.get(title)
            if not user or not book:
                self.stdout.write(self.style.WARNING(
                    f'    ! Skipping borrow: {username} / {title} (not found)'
                ))
                continue

            borrow_date = today - timedelta(days=days_borrowed)
            due_date    = borrow_date + timedelta(days=14)

            if BorrowRecord.objects.filter(student=user, book=book, borrow_date=borrow_date).exists():
                continue

            record = BorrowRecord(
                student=user, book=book,
                borrow_date=borrow_date,
                due_date=due_date,
                status=status,
            )
            if status == 'returned' and days_returned is not None:
                record.return_date = today - timedelta(days=days_returned)
            record.save()

            # keep available_copies accurate
            if status == 'borrowed' and book.available_copies > 0:
                book.available_copies -= 1
                book.save()

            self.stdout.write(
                f'    + [{status:8s}] {username:15s} -> {title[:40]}'
            )

    def _seed_reviews(self, users, books):
        self.stdout.write('  Creating reviews...')
        for username, title, rating, comment in REVIEWS:
            user = users.get(username)
            book = books.get(title)
            if not user or not book:
                self.stdout.write(self.style.WARNING(
                    f'    ! Skipping review: {username} / {title} (not found)'
                ))
                continue

            # Only allow review if user has a returned borrow for this book
            has_returned = BorrowRecord.objects.filter(
                student=user, book=book, status='returned'
            ).exists()
            if not has_returned:
                self.stdout.write(self.style.WARNING(
                    f'    ! Skipping review (no returned borrow): {username} / {title}'
                ))
                continue

            _, created = Review.objects.get_or_create(
                student=user, book=book,
                defaults={'rating': rating, 'comment': comment},
            )
            if created:
                self.stdout.write(f'    + [{rating}/5] {username} -> {title[:35]}')
