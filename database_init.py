from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create Myself
User1 = User(name="Cheng Wang", email="njuwangcheng@gmail.com",
             picture='https://lh5.googleusercontent.com/-f8KfwnBrpW0/AAAAAAAAAAI/AAAAAAAAAOk/hh5a-LA7oQ8/photo.jpg')
session.add(User1)
session.commit()


#items for climbing
category1 = Category(user_id=1,name = "Climbing")

session.add(category1)
session.commit()


item1 = Item(user_id=1,name = "Climbing Ropes", 
             description = """This low-stretch PMI E-Z Bend Sport static rope 
is a favorite of cavers and search-and-rescue teams.""",
             category = category1)

session.add(item1)
session.commit()


item2 = Item(user_id=1,name = "Climbing Packs", 
             description = """Built with versatility in mind, this waterproof 
pack keeps your gear dry without fumbling for a raincover, and easily carries 
everything you need for an epic day on the mountain or crag.""",
             category = category1)

session.add(item2)
session.commit()


#items for cycles
category2 = Category(user_id=1,name = "Cycle")

session.add(category2)
session.commit()


item1 = Item(user_id=1,name = "Quick Carbon 1 Bike", 
             description = "The Quick Carbon 1 Bike blends the featherlight performance of an all-carbon frame with the easy handling of an upright, flat-bar bike for urban rides, commutes and tours.",
             category = category2)

session.add(item1)
session.commit()

item2 = Item(user_id=1,name = "Novara Randonee Bike", 
             description = "With a sleek look, our iconic pavement-touring Randonee bike features a smooth-riding chromoly frame and accessory compatibility that makes it a true classic.",
             category = category2)

session.add(item2)
session.commit()


#items for Snowboards
category3 = Category(user_id=1,name = "Snowboards")

session.add(category3)
session.commit()

item1 = Item(user_id=1, name = "Capita Charlie Slasher Snowboard", 
             description = "Updated with Dynaweave fiberglass and a new Dual Species core, this board features a 20mm tapered tail and rockered nose, transforming tiring powder days into long-lasting, effortless ones.",
             category = category3)             

session.add(item1)
session.commit()

item2 = Item(user_id=1, name = "Burton Clash Snowboard", 
             description = "Easy to ride and even easier on the wallet, the Burton Clash is ideal for mastering the basics and blasting your first airs.",
             category = category3)   
          
session.add(item2)
session.commit()

#print session.query(Category).all()

nm = 'Snowboards'

print session.query(Category).filter_by(name=nm).first().id

for item  in session.query(Item).filter_by(category_id = "1").all():
    print item.name, item.user_id


print "Added User and items!"