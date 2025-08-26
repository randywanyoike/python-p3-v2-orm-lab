from __init__ import CURSOR, CONN

class Review:
    
    # Dictionary to keep track of all Review instances
    all = {}
    
    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary  
        self.employee_id = employee_id
        
        # Add to class-level dictionary
        if id is not None:
            type(self).all[id] = self
    
    def __repr__(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, Employee: {self.employee_id}>"
    
    @property
    def year(self):
        return self._year
    
    @year.setter
    def year(self, year):
        if not isinstance(year, int):
            raise ValueError("Year must be an integer")
        if year < 2000:
            raise ValueError("Year must be >= 2000")
        self._year = year
    
    @property
    def summary(self):
        return self._summary
    
    @summary.setter
    def summary(self, summary):
        if not isinstance(summary, str) or len(summary) == 0:
            raise ValueError("Summary must be a non-empty string")
        self._summary = summary
    
    @property
    def employee_id(self):
        return self._employee_id
    
    @employee_id.setter
    def employee_id(self, employee_id):
        # Check if employee exists in database
        sql = "SELECT COUNT(*) FROM employees WHERE id = ?"
        count = CURSOR.execute(sql, (employee_id,)).fetchone()[0]
        if count == 0:
            raise ValueError("employee_id must reference an employee in the database")
        self._employee_id = employee_id
    
    @classmethod
    def create_table(cls):
        """Create the reviews table if it doesn't exist"""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()
    
    @classmethod
    def drop_table(cls):
        """Drop the reviews table if it exists"""
        sql = "DROP TABLE IF EXISTS reviews"
        CURSOR.execute(sql)
        CONN.commit()
        cls.all = {}
    
    def save(self):
        """Save the Review instance to the database and set the instance id"""
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()
        
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self
    
    @classmethod
    def create(cls, year, summary, employee_id):
        """Create a new Review instance and save it to the database"""
        review = cls(year, summary, employee_id)
        review.save()
        return review
    
    @classmethod
    def instance_from_db(cls, row):
        """Create a Review instance from a database row"""
        if row is None:
            return None
        
        id, year, summary, employee_id = row
        
        # Check if instance already exists in our dictionary
        if id in cls.all:
            # Update existing instance with database values
            instance = cls.all[id]
            instance._year = year
            instance._summary = summary
            instance._employee_id = employee_id
        else:
            # Create new instance
            instance = cls(year, summary, employee_id, id)
        
        return instance
    
    @classmethod
    def find_by_id(cls, id):
        """Find a Review instance by id"""
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row)
    
    def update(self):
        """Update the instance's corresponding database record"""
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()
    
    def delete(self):
        """Delete the instance's corresponding database record"""
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        
        # Remove from class dictionary
        if self.id in type(self).all:
            del type(self).all[self.id]
        
        # Set id to None to indicate it's no longer in database
        self.id = None
    
    @classmethod
    def get_all(cls):
        """Return a list of Review instances for every record in the database"""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]