
from . import dbfunctions as db


class User:
    def __init__ (self, user_id, email, fname, lname, DOB, location, gender, photo, phone, password):
        self._user_id = user_id
        self._email = email
        self._fname = fname
        self._lname = lname
        self._DOB = DOB
        self._location = location
        self._gender = gender
        self._photo = photo
        self._phone = phone
        self._password = password

    def __str__(self):
        return 'Object for user {}'.format(self.name)

    '''
    Everything after this point needs to be updated in the database too!
    '''
#********************************************************************************
#********************************************************************************
#Return fields
#********************************************************************************
#********************************************************************************
    def get_user_id(self):
        return self._user_id

    def get_email(self):
        return self._email

    def get_first_name(self):
        return self._fname

    def get_last_name(self):
        return self._lname

    def get_DOB(self):
        return self._DOB

    def get_age(self):
        #Calulate age from DOB
        return self._DOB

    def get_location(self):
        #Split into long/lat
        return self._location

    def get_gender(self):
        return self._gender

    def get_photo(self):
        #Ask Bruce
        return self._photo

    def get_phone(self):
        return self._phone

    def get_password(self):
        return self._password
#********************************************************************************
#********************************************************************************
#Sign in and log in
#********************************************************************************
#********************************************************************************
    
    @classmethod
    def email_exists(klass, email):
        if db.select(email, None, 'user'):
            return True
        else:
            return False    

    @classmethod
    def create_user(klass, columnvaluedict):
        db.insert('user', columnvaluedict)
        newUser = User(columnvaluedict.get('user_id'), columnvaluedict.get('email'), columnvaluedict.get('fname'), columnvaluedict.get('lname'), columnvaluedict.get('DOB'), columnvaluedict.get('location'), columnvaluedict.get('gender'), columnvaluedict.get('photo'), columnvaluedict.get('phone'), columnvaluedict.get('password'))
        return newUser

    @classmethod
    def get_person_by_id(klass, user_id):
        whereClause = 'user_id = ' + user_id
        person_dict = db.select('user', whereClause, 'user_id', 'email', 'fname', 'lname', 'DOB', 'location', 'gender', 'phone')
        new_user = User(columnvaluedict.get('user_id'), columnvaluedict.get('email'), columnvaluedict.get('fname'), columnvaluedict.get('lname'), columnvaluedict.get('DOB'), columnvaluedict.get('location'), columnvaluedict.get('gender'), columnvaluedict.get('photo'), columnvaluedict.get('phone'), columnvaluedict.get('password'))
        return new_user
        
    @classmethod
    def get_person_by_email(klass, email):
        whereClause = 'email = ' + email
        person_dict = db.select('user', whereClause, 'user_id', 'email', 'fname', 'lname', 'DOB', 'location', 'gender', 'phone')
        new_user = User(columnvaluedict.get('user_id'), columnvaluedict.get('email'), columnvaluedict.get('fname'), columnvaluedict.get('lname'), columnvaluedict.get('DOB'), columnvaluedict.get('location'), columnvaluedict.get('gender'), columnvaluedict.get('photo'), columnvaluedict.get('phone'), columnvaluedict.get('password'))
        return new_user

    @classmethod
    def verify_password(klass, email, password):
        whereClause = 'email = ' + email
        inDb = select('user', whereClause, 'password')
        if inDb:
            if password == inDb:
                return True
            else:
                return False #Incorrect password
        else:
            return False #Incorrect email


# print (User.email_exists('george.com'))

# myDictionary = {'user_id' : 3, 'email' : 'george.com', 'fname' : 'george', 'lname' : 'bob', 'DOB' : '1999-12-09', 'location' : -4.999, 78.908, 'gender' : 'M', 'photo': , phone, password}
# newUser = User.create_user(myDictionary)
# print (newUser)


#********************************************************************************
#********************************************************************************
#Fun stuff
#********************************************************************************
#********************************************************************************
'''
#Name Modifications
    def updateName(self, newName):
        self.name = newName

#Age Modifications    
    def updateAge(self, newAge):
        self.age = newAge

#Location Modifications
    def updateLocation(self, newLocation):
        self.location = newLocation

#Gender Modifications
    def updateGender(self, newGender):
        self.gender = newGender

#Skills Modifications
    def updateSkills(self, newSkills):
        self.skills = newSkills

    def appendSkill(self, newSkill):
        self.skills = self.skills.append(newSkill)

#Photo Modifications
    def updatePhoto(self, newPhoto):
        self.photo = newPhoto

#Contact Modifications
    def updateContact(self, newContact):
        self.contact = newContact
'''
