from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in the local dictionary using table row's PK as the dictionary key"""
        with CONN:
            CURSOR.execute(
                "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
                (self.year, self.summary, self.employee_id),
            )
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        new_review = cls(year, summary, employee_id)
        new_review.save()
        return new_review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        review_id = row[0]  # Assuming the id is the first element in the tuple
        if review_id not in cls.all:
            review = cls(row[1], row[2], row[3], review_id)
            cls.all[review_id] = review
        return cls.all[review_id]


    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        with CONN:
            CURSOR.execute("SELECT * FROM reviews WHERE id=?", (id,))
            row = CURSOR.fetchone()
            return cls.instance_from_db(row) if row else None


    def update(self):
        """Update the table row corresponding to the current Review instance."""
        with CONN:
            CURSOR.execute(
                "UPDATE reviews SET year=?, summary=?, employee_id=? WHERE id=?",
                (self.year, self.summary, self.employee_id, self.id),
            )

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        with CONN:
            CURSOR.execute("DELETE FROM reviews WHERE id=?", (self.id,))
            del Review.all[self.id]
            self.id = None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        with CONN:
            CURSOR.execute("SELECT * FROM reviews")
            rows = CURSOR.fetchall()
            return [cls.instance_from_db(row) for row in rows]

