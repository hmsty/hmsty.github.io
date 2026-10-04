"""Books shown on /reading/.

Section -> subsection -> [(title, author)]. Leave the author as "" when the
subsection is already named after the author.
"""

READING = {
    "economics & markets": {
        "thomas sowell": [
            ("Basic Economics", ""),
            ("Applied Economics", ""),
            ("Knowledge and Decisions", ""),
            ("The Vision of the Anointed", ""),
            ("Economic Facts and Fallacies", ""),
            ("Wealth, Poverty and Politics", ""),
            ("Discrimination and Disparities", ""),
            ("Black Rednecks and White Liberals", ""),
            ("Intellectuals and Race", ""),
            ("The Housing Boom and Bust", ""),
            ("Social Justice Fallacies", ""),
            ("Charter Schools and Their Enemies", ""),
        ],
        "classical liberal": [
            ("The Road to Serfdom", "F. A. Hayek"),
            ("Free to Choose", "Milton & Rose Friedman"),
            ("Capitalism and Freedom", "Milton Friedman"),
            ("On Liberty", "John Stuart Mill"),
            ("The Theory of Moral Sentiments", "Adam Smith"),
            ("Capitalism in America", "Alan Greenspan & Adrian Wooldridge"),
        ],
        "investing & macro": [
            ("The Intelligent Investor", "Benjamin Graham"),
            ("The Bogleheads' Guide to Investing", "Larimore, Lindauer & LeBoeuf"),
            ("Liar's Poker", "Michael Lewis"),
        ],
        "tech & startups": [
            ("Zero to One", "Peter Thiel"),
            ("Read Write Own", "Chris Dixon"),
            ("The Deep Learning Revolution", "Terrence Sejnowski"),
        ],
    },
    "decisions & risk": {
        "behavioral economics": [
            ("Thinking, Fast and Slow", "Daniel Kahneman"),
            ("Nudge", "Richard Thaler & Cass Sunstein"),
            ("Behavioral Economics", "Edward Cartwright"),
            ("Freakonomics", "Steven Levitt & Stephen Dubner"),
            ("SuperFreakonomics", "Steven Levitt & Stephen Dubner"),
        ],
        "risk & uncertainty": [
            ("Fooled by Randomness", "Nassim Nicholas Taleb"),
            ("The Black Swan", "Nassim Nicholas Taleb"),
            ("Skin in the Game", "Nassim Nicholas Taleb"),
            ("Thinking in Bets", "Annie Duke"),
        ],
        "malcolm gladwell": [
            ("Outliers", ""),
            ("The Tipping Point", ""),
            ("David and Goliath", ""),
            ("What the Dog Saw", ""),
            ("Talking to Strangers", ""),
        ],
    },
    "science & philosophy": {
        "philosophy of science": [
            ("The Beginning of Infinity", "David Deutsch"),
            ("All Life Is Problem Solving", "Karl Popper"),
            ("Gödel, Escher, Bach", "Douglas Hofstadter"),
        ],
        "science": [
            ("Behave", "Robert M. Sapolsky"),
            ("On the Origin of Species", "Charles Darwin"),
            ("The Evolution of Everything", "Matt Ridley"),
            ("A Short History of Nearly Everything", "Bill Bryson"),
        ],
        "steven pinker": [
            ("Enlightenment Now", ""),
            ("The Better Angels of Our Nature", ""),
            ("The Blank Slate", ""),
        ],
        "philosophy": [
            ("Meditations", "Marcus Aurelius"),
            ("The Present Alone Is Our Happiness", "Pierre Hadot"),
            ("Tao Te Ching", "Lao Tzu"),
            ("Man's Search for Meaning", "Viktor Frankl"),
            ("The Book of Life", "J. Krishnamurti"),
            ("The Book", "Alan Watts"),
            ("What We Owe the Future", "William MacAskill"),
            ("Philosophy: Who Needs It", "Ayn Rand"),
        ],
        "anthologies": [
            ("Contemporary Debates in Epistemology", "Steup, Turri & Sosa, eds."),
            ("Readings in Ancient Greek Philosophy", "Cohen, Curd & Reeve, eds."),
            ("Modern Philosophy: An Anthology of Primary Sources", "Ariew & Watkins, eds."),
        ],
    },
    "other nonfiction": {
        "": [
            ("The Doors of Perception", "Aldous Huxley"),
            ("The Wisdom of Psychopaths", "Kevin Dutton"),
            ("Hidden Potential", "Adam Grant"),
            ("Based on a True Story", "Norm Macdonald"),
            ("Thinking Inside the Box", "Adrienne Raphel"),
        ],
    },
    "fiction": {
        "vladimir nabokov": [
            ("The Annotated Lolita", ""),
            ("Pale Fire", ""),
            ("Pnin", ""),
            ("Despair", ""),
            ("Invitation to a Beheading", ""),
            ("The Luzhin Defense", ""),
        ],
        "ernest hemingway": [
            ("The Sun Also Rises", ""),
            ("For Whom the Bell Tolls", ""),
            ("The Old Man and the Sea", ""),
            ("The Snows of Kilimanjaro and Other Stories", ""),
        ],
        "ayn rand": [
            ("Atlas Shrugged", ""),
            ("The Fountainhead", ""),
            ("We the Living", ""),
            ("Anthem", ""),
        ],
        "dystopia & sci-fi": [
            ("Brave New World", "Aldous Huxley"),
            ("1984", "George Orwell"),
            ("Fahrenheit 451", "Ray Bradbury"),
            ("The Moon Is a Harsh Mistress", "Robert A. Heinlein"),
            ("Solaris", "Stanisław Lem"),
        ],
        "everything else": [
            ("Catch-22", "Joseph Heller"),
            ("All Quiet on the Western Front", "Erich Maria Remarque"),
            ("Slaughterhouse-Five", "Kurt Vonnegut"),
            ("As I Lay Dying", "William Faulkner"),
            ("The Grapes of Wrath", "John Steinbeck"),
            ("A Prayer for Owen Meany", "John Irving"),
            ("The World According to Garp", "John Irving"),
        ],
    },
}
