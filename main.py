#The Foursquare API key can be found on https://developer.foursquare.com/docs/api/getting-started.
#You will need an existing Foursquare account or you can make a new one to have a Developer Account and access the
#API key.




import webapp2
import urllib, urllib2, webbrowser, json
#import urllib.parse, urllib.request, urllib.error, json
import jinja2, os, logging

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("In MainHandler")

        template_values = {}
        template_values['page_title'] = "LetsGo"
        template = JINJA_ENVIRONMENT.get_template('gettinginput.html')
        self.response.write(template.render(template_values))

def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        logging.info('The server couldn\'t fulfill the request')
        logging.info('Error code: %s',e.code)
    except urllib2.URLError, e:
        logging.info('We failed to reach a server')
        logging.info('Reason: %s',e.reason)
    return None

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)




def foursquareREST(baseurl='https://api.foursquare.com/v2/venues/',
                   method = 'explore',
                   id = client_id,
                   secretkey = client_secret,
                   params = {},
                   ):
    #params['method'] = method
    params['v'] = '20171108' #today's date
    params['client_id'] = id
    params['client_secret'] = secretkey
    url = baseurl + method + '?' + urllib.urlencode(params) #have to take out parse when on app engine
    logging.info(url)
    return(safeGet(url))


def getVenueRecommendations(near, radius, query, price=''):


    data_retrieved = foursquareREST(params={'near': near,
                                     'radius': radius,
                                     'query': query,
                                     'price': price,
                                     'venuePhotos': True,
                                     'sortByDistance': True
                                     })

    if (data_retrieved !=None):
        data_read = data_retrieved.read()
        data_load = json.loads(data_read)

    venues = data_load['response']['groups'][0]['items']
    return venues

def getVenueIDList(venues):
    idlist = [venue_ids['venue']['id'] for venue_ids in venues]
    return idlist

def getVenueInfo(id):
    data = foursquareREST(method=id)
    if (data !=None):
        data_read = data.read()
        data_jsonload = json.loads(data_read)
        venue_info = data_jsonload['response']['venue']
        return venue_info
    else:
        return None


class Venue():
    def __init__(self, venuesdict):
        self.name = venuesdict['name']
        if 'address' in venuesdict['location']:
            self.address = venuesdict['location']['address']
        if 'rating' in venuesdict:
            self.rating = venuesdict['rating']
        else:
            self.rating = -1
        self.lat_long = (venuesdict['location']['lat'], venuesdict['location']['lng'])
        self.fs_url = venuesdict['canonicalUrl']
        if 'url' in venuesdict:
            self.website_url = venuesdict['url']
        if 'bestPhoto' in venuesdict:
            url = venuesdict['bestPhoto']['prefix'] + str(venuesdict['bestPhoto']['height']) + 'x' + str(venuesdict['bestPhoto']['width']) + venuesdict['bestPhoto']['suffix']
            self.photo = url


class responseHandler(webapp2.RequestHandler):
    def post(self):
        #getting user inputs
        location = self.request.get('location')
        food = self.request.get('food')
        entertainment = self.request.get('entertainment')
        food_price_tier = self.request.get('food_price_tier')


        vals = {} #this is for output
        vals['page_title']='Choose an itinerary for ' + location
        vals['location'] = location
        vals['food'] = food
        vals['entertainment'] = entertainment
        vals['food_price_tier'] = food_price_tier



        if location:
            food_venues_chosen = getVenueRecommendations(location, 500, food, food_price_tier)
            food_venues = [Venue(getVenueInfo(venue_id)) for venue_id in getVenueIDList(food_venues_chosen)]

            ent_venues_chosen = getVenueRecommendations(location, 500, entertainment)
            ent_venues = [Venue(getVenueInfo(venue_id)) for venue_id in getVenueIDList(ent_venues_chosen)]

            food_venues_by_rating = sorted(food_venues, key=lambda food: food.rating, reverse=True)
            give_food_venues = []
            give_ent_venues = []
            ent_venues_by_rating = sorted(ent_venues, key=lambda ent: ent.rating, reverse=True)


            var = 0
            for foodvenues in food_venues_by_rating[var:var+3]:
                give_food_venues.append(foodvenues)

            for entvenues in ent_venues_by_rating[var:var+3]:
                give_ent_venues.append(entvenues)

            vals['give_food_venues'] = give_food_venues
            vals['give_ent_venues'] = give_ent_venues

            give_venues = []
            for venues in give_food_venues:
                give_venues.append(venues)
            for venues in give_ent_venues:
                give_venues.append(venues)

            logging.info(give_venues)

            sorted_give_venues = [0, 1, 2, 3, 4, 5]

            sorted_give_venues[0] = give_venues[0]
            sorted_give_venues[1] = give_venues[3]
            sorted_give_venues[2] = give_venues[1]
            sorted_give_venues[3] = give_venues[4]
            sorted_give_venues[4] = give_venues[2]
            if len(give_venues) == 6:
                sorted_give_venues[5] = give_venues[5]
            else:
                del sorted_give_venues[5]

            vals['sorted_give_venues'] = sorted_give_venues


            template = JINJA_ENVIRONMENT.get_template('responsepage.html')
            self.response.write(template.render(vals))
        else:
            template = JINJA_ENVIRONMENT.get_template('gettinginput.html')
            self.response.write(template.render(vals))


application = webapp2.WSGIApplication([('/gresponse', responseHandler),('/.*', MainHandler)], debug=True)





























