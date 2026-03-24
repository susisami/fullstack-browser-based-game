from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql, random, requests
from geopy.distance import geodesic
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash

program = Flask(__name__)
CORS(program)


# Yliluokka SQL-yhteydelle
class SqlConnection:
    def __init__(self, host, port, database, user, password, autocommit):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.autocommit = autocommit

    def connection(self):
        connection = pymysql.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
            autocommit=self.autocommit
        )
        return connection


# Aliluokka, mikä hakee aloitus tiedot käyttäjälle
class StarterInformation(SqlConnection):
    def __init__(self, host, port, database, user, password, autocommit):
        super().__init__(host, port, database, user, password, autocommit)

    def connection(self):
        return super().connection()

    def test_username(self, name):
        self.name = name

        with self.connection().cursor() as cursor:
            sql = """SELECT nick from game where nick = %s"""
            cursor.execute(sql, (name,))
            result = cursor.fetchone()

            if result:
                self.free_user_nick = False
            else:
                self.free_user_nick = True
            return self.free_user_nick

    def starting_money(self):
        self.balance = int(random.randint(5000, 20000))
        return self.balance

    def starting_airport(self):
        try:
            with self.connection().cursor() as cursor:
                sql = f"SELECT name FROM airport WHERE airport.type NOT IN ('heliport', 'closed', 'seaplane_base', 'balloonport') ORDER BY RAND() LIMIT 1;"
                cursor.execute(sql)
                result = cursor.fetchone()

                if result:
                    self.airport_name = result[0]
                    return self.airport_name
                else:
                    return "SQL-Query fetched no results."

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"

    def starting_icao(self, airport):
        self.airport = airport

        try:
            with self.connection().cursor() as cursor:
                sql = """SELECT ident FROM airport WHERE airport.name = %s"""
                cursor.execute(sql, (airport))
                result = cursor.fetchone()

                if result:
                    self.airport_ident = result[0]
                    return self.airport_ident
                else:
                    return "SQL-Query fetched no results."

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"

    def starting_country(self, airport):
        self.airport = airport

        try:
            with self.connection().cursor() as cursor:
                sql = """SELECT country.name FROM country, airport WHERE airport.name = %s and airport.iso_country = country.iso_country"""
                cursor.execute(sql, (airport))
                result = cursor.fetchone()

                if result:
                    self.country = result[0]
                    return self.country
                else:
                    print("SQL-Query fetched no results.")

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"

    def starting_continent(self, airport):
        self.airport = airport

        try:
            with self.connection().cursor() as cursor:
                sql = """SELECT country.continent FROM country, airport WHERE airport.name = %s and airport.iso_country = country.iso_country"""
                cursor.execute(sql, (airport))
                result = cursor.fetchone()

                if result:
                    self.continent = result[0]
                    return self.continent
                else:
                    return 'SQL-Query fetched no results.'

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"

    def starting_lat_lon(self, airport):
        self.lat_lon = []
        self.airport = airport

        try:
            with self.connection().cursor() as cursor:
                sql = """SELECT latitude_deg, longitude_deg FROM airport WHERE airport.name = %s"""
                cursor.execute(sql, (airport))
                result = cursor.fetchone()

                if result:
                    self.lat_lon.append(float(result[0]))
                    self.lat_lon.append(float(result[1]))
                    return self.lat_lon
                else:
                    return "SQL-Query fetched no results."

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"

    def insert_new_data(self, stdata, generated_data):
        self.stdata = stdata
        self.generated_data = generated_data
        try:
            with self.connection().cursor() as cursor:
                hashed_password = generate_password_hash(stdata['Password'])

                sql = """INSERT INTO game (nick, password, balance, current_airport, current_country, current_icao_code, current_continent, current_lat, current_lon, visited_countries, distance_km)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

                cursor.execute(sql, (
                    stdata['Username'],
                    hashed_password,
                    generated_data['Balance'],
                    generated_data['Airport'],
                    generated_data['Country'],
                    generated_data['ICAO'],
                    generated_data['Continent'],
                    generated_data['Latitude & Longitude'][0],
                    generated_data['Latitude & Longitude'][1],
                    generated_data['Visited Countries'],
                    generated_data['Traveled Kilometers'],
                ))

                return [stdata, generated_data]

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"


# Aliluokka, mikä päivittää käyttäjän tiedot tietokantaan saaden datan listana clientilta.
class UpdateUser(SqlConnection):
    def __init__(self, host, port, database, user, password, autocommit):
        super().__init__(host, port, database, user, password, autocommit)

    def connection(self):
        return super().connection()

    def adjust_country(self, current_icao):
        self.current_airport = current_icao

        try:
            with self.connection().cursor() as cursor:
                sql = """SELECT country.name FROM country, airport WHERE airport.ident = %s and airport.iso_country = country.iso_country"""
                cursor.execute(sql, (current_icao,))
                result = cursor.fetchone()

                if result:
                    self.country = result[0]
                    return self.country
                else:
                    print("SQL-Query fetched no results.")

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"

    def update(self, datalist):
        self.datalist = datalist
        try:
            with self.connection().cursor() as cursor:
                # Päivitetään käyttäjätiedot tietokantaan (Tätä ennen täytyy tapahtua rahanmuutosoperaatio, kilometrien muutos jne. niiden omassa luokassa):
                updatesql = """
                    UPDATE game 
                    SET balance = %s, 
                        current_airport = %s, 
                        current_country = %s,  
                        current_icao_code = %s, 
                        current_continent = %s, 
                        current_lat = %s,
                        current_lon = %s,
                        visited_countries = %s + 1,
                        distance_km = %s
                    WHERE nick = %s;
                    """
                cursor.execute(updatesql, (
                    datalist[1],
                    datalist[2],
                    datalist[3],
                    datalist[4],
                    datalist[6],
                    datalist[7],
                    datalist[8],
                    datalist[9],
                    datalist[10],
                    datalist[0],
                ))
                return {'Updated Data': datalist}

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"

    def fetch_updated_user(self, username):
        self.username = username

        try:
            with self.connection().cursor() as cursor:
                sql = """
                SELECT nick, balance, current_airport, current_country, current_icao_code, current_continent, current_lat, current_lon, visited_countries, distance_km 
                FROM game
                WHERE nick = %s
                """
                cursor.execute(sql, (username,))
                result = cursor.fetchone()

                if result:
                    self.loaded_data = {
                        'Username': result[0],
                        'Balance': result[1],
                        'Airport': result[2],
                        'Country': result[3],
                        'ICAO': result[4],
                        'Continent': result[5],
                        'Latitude': result[6],
                        'Longitude': result[7],
                        'Visited Countries': result[8],
                        'Traveled Kilometers': result[9]
                    }
                    return self.loaded_data

                else:
                    return 'User not found after update.'

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"


# Aliluokka, jota käytetään käyttäjätietojen hakuun ladatessa jo aloitettua peliä.
class LoadGame(SqlConnection):
    def __init__(self, host, port, database, user, password, autocommit):
        super().__init__(host, port, database, user, password, autocommit)

    def connection(self):
        return super().connection()

    def test_user_name_password(self, nick, pwd):
        self.nick = nick
        self.pwd = pwd

        try:
            with self.connection().cursor() as cursor:
                sql = """SELECT password 
                         FROM game
                         WHERE nick = %s"""
                cursor.execute(sql, (nick,))

                result = cursor.fetchone()

                if result:
                    stored_password_hash = result[0]
                    if check_password_hash(stored_password_hash, pwd):
                        self.found_user = True
                    else:
                        self.found_user = False
                else:
                    self.found_user = False

                return self.found_user

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"

    def load_save(self, nickname):
        self.nickname = nickname

        try:
            with self.connection().cursor() as cursor:
                sql = """SELECT nick, balance, current_airport, current_country, current_icao_code, current_continent, current_lat, current_lon, visited_countries, distance_km 
                FROM game
                WHERE nick = %s
                """

                cursor.execute(sql, (
                    nickname,
                ))
                result = cursor.fetchone()
                if result:
                    self.loaded_data_dict = {
                        'Username': result[0],
                        'Balance': result[1],
                        'Airport': result[2],
                        'Country': result[3],
                        'ICAO': result[4],
                        'Continent': result[5],
                        'Latitude': result[6],
                        'Longitude': result[7],
                        'Visited Countries': result[8],
                        'Traveled kilometers': result[9]
                    }
                    return self.loaded_data_dict

                else:
                    return 'SQL-Query Error.'

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"

        # Aliluokka, missä lasketaan etäisyys käyttäjän nykyisen sijainnin ja valitun sijainnin välillä, muutetaan käyttäjän balance vastaamaan etäisyyden generoimaa rahamäärää (balancen ja generoidun rahamäärän EROTUS) ja luodaan tarvittu data [100] satunnaisen lentokentän merkkaamiseksi leaflet-karttaan. GenerateTravel metodit ajetaan ennen UpdateUser-luokan metodeja, jotta päivitetty data on oikea. Hyödynnä tässä muita jo luotuja aliluokkia esim. käyttäjätietojen päivittämiseen, sekä OHJ1 funktioita.


# Aliluokka juoksevan pelaajadatan (kuljetut kilometrit, rahamäärä, vieraillut lentokentät jne.) päivitykseen, sekä seuraavien mahdollisten lentokenttien hakemiseksi.
class GenerateTravel(SqlConnection):
    def __init__(self, host, port, database, user, password, autocommit):
        super().__init__(host, port, database, user, password, autocommit)

    def connection(self):
        return super().connection()

    def list_airports(self, limit=30):
        try:
            with self.connection().cursor() as cursor:
                sql = """SELECT name, latitude_deg, longitude_deg, ident, type, elevation_ft, continent, iso_country, iso_region, municipality, scheduled_service, gps_code
                        FROM airport
                        WHERE type NOT IN ('heliport', 'closed', 'seaplane_base', 'balloonport')
                        ORDER BY RAND()
                        LIMIT %s"""
                cursor.execute(sql, (limit,))
                return [{
                    'name': row[0],
                    'lat': float(row[1]),
                    'lon': float(row[2]),
                    'icao': row[3],
                    'type': row[4],
                    'elevation_ft': row[5],
                    'continent': row[6],
                    'country': row[7],
                    'country_region': row[8],
                    'city': row[9],
                    'service-schedule': row[10],
                    'gps-code': row[11]
                } for row in cursor.fetchall()]
        except Exception as e:
            return f"Virhe lentokenttien listauksessa: {e}"

    def current_icao(self, username):
        self.username = username

        try:
            with self.connection().cursor() as cursor:
                icao_code_query = "SELECT current_icao_code FROM game WHERE nick = %s;"
                cursor.execute(icao_code_query, (username,))
                result = cursor.fetchone()

                if result:
                    return result[0]
                else:
                    return f"Pelaajalle {username} ei löytynyt ICAO-koodia."

        except Exception as e:
            return f"Virhe ICAO-koodin haussa: {e}"

    def get_airport_coordinates(self, icao_code):
        self.icao_code = icao_code

        try:
            with self.connection().cursor() as cursor:
                sql = """SELECT latitude_deg, longitude_deg 
                         FROM airport 
                         WHERE ident = %s"""
                cursor.execute(sql, (icao_code,))
                result = cursor.fetchone()
                if result:
                    return float(result[0]), float(result[1])
                return f'No latitude and longitude with the given icao :{icao_code}'

        except Exception as e:
            return f"Virhe koordinaattien haussa: {e}"

    def calculate_distance(self, new_icao, old_icao):
        self.new_icao = new_icao
        self.old_icao = old_icao

        coords_1 = self.get_airport_coordinates(new_icao)
        coords_2 = self.get_airport_coordinates(old_icao)

        if coords_1 and coords_2:
            distance = geodesic(coords_1, coords_2).kilometers
            return int(distance)


#Luokka reaaliaikaisen datan hakuun käyttäjän sen hetkisestä sijainnista.
class GenerateRealTimeData:
    def __init__(self, current_lat, current_lon):
        self.apikey = 'd77d844e9f5422bb32d407fdd22901f6'
        self.current_lat = current_lat
        self.current_lon = current_lon
        self.temperature_k = 0
        self.temperature_c = 0
        self.weather_condition = ''
        self.weatherdict = {}

    def fetch_real_time_data(self):
        # Reaaliaikaisen datan hakeminen:
        query = f"https://api.openweathermap.org/data/2.5/weather?lat={self.current_lat}&lon={self.current_lon}&limit=1&appid={self.apikey}"
        weather_data = requests.get(query).json()

        # Reaaliaikainen data pelaajan nykyisestä olinpaikasta (Tähän voi vielä lisätä jotain, jos tulee mieleen):
        self.temperature_k = int((weather_data['main']['temp']))
        self.weather_condition = (weather_data['weather'][0]['main'])
        self.temperature_c = (round(self.temperature_k - 273.15))

        # Datan tallennus sanakirjaan:
        self.weatherdict.update({'Latitude': self.current_lat})
        self.weatherdict.update({'Longitude': self.current_lon})
        self.weatherdict.update({'Temperature_Condition': self.weather_condition})
        self.weatherdict.update({'Temperature_Kelvin': self.temperature_k})
        self.weatherdict.update({'Temperature_Celsius': self.temperature_c})

        return self.weatherdict


# Aliluokka, mikä käsittää useita eri yksittäisiä metodeja, mm. käyttäjän palautteenannon, leaderboardsin haun ja käyttäjän poistamisen.
class Utility(SqlConnection):
    def __init__(self, host, port, database, user, password, autocommit):
        super().__init__(host, port, database, user, password, autocommit)

    def connection(self):
        return super().connection()

    def send_feedback(self, datalist):
        self.datalist = datalist
        self.feedback = ''
        try:
            with self.connection().cursor() as cursor:
                sql = """INSERT INTO feedback (first_name, last_name, nickname, contact_email, phone_number, country, feedback_text)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                cursor.execute(sql, (
                    datalist[0],
                    datalist[1],
                    datalist[2],
                    datalist[3],
                    datalist[4],
                    datalist[5],
                    datalist[6],
                ))

                select = """SELECT *
                            FROM feedback
                            WHERE nickname = %s"""
                cursor.execute(select, (
                    datalist[2],
                ))

                result = cursor.fetchone()

                if result:
                    self.feedback = True
                else:
                    self.feedback = False
                return self.feedback

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"

    def show_leaderboard(self):
        try:
            with self.connection().cursor() as cursor:
                # Modified query to ensure proper ordering
                sql = """SELECT nick AS username, balance 
                         FROM game 
                         WHERE balance > 0 
                         ORDER BY balance DESC 
                         LIMIT 10;"""  # Limit results

                cursor.execute(sql)
                result = cursor.fetchall()

                if not result:
                    return []  # Return empty list instead of string

                return result

        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return []  # Return empty list on error

        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def delete_user(self, username):
        self.username = username

        try:
            with self.connection().cursor() as cursor:
                sql = """DELETE FROM game WHERE nick = %s"""
                cursor.execute(sql, (username,))

                sql2 = """SELECT * FROM game where nick = %s"""
                cursor.execute(sql2, (username,))

                result = cursor.fetchone()
                if result == None:
                    return True
                else:
                    return False

        except pymysql.MySQLError as e:
            return f"Tietokantavirhe: {e}"

        except Exception as e:
            return f"Satunnaisvirhe: {e}"


#Luokan metodi hakee REST openapia käyttäen satunnaisen kysymyksen, mikä liittyy pelaajan sen hetken maahan.     
class CountryQuiz:
    def __init__(self, current_country):
        self.current_country = current_country
        self.question = None

    def fetch_country_quiz(self):
        try:
            # Add timeout and better error handling
            resp = requests.get(
                f"https://restcountries.com/v3.1/name/{self.current_country}",
                timeout=5
            )
            resp.raise_for_status()
            data = resp.json()

            if not data or not isinstance(data, list):
                return self._create_fallback_question()

            # Use the first valid country data
            country = data[0]
            return self._create_question_from_data(country)

        except Exception as e:
            print(f"Error fetching country data: {e}")
            return self._create_fallback_question()

    def _create_question_from_data(self, country):
        try:
            name = country.get("name", {}).get("common", "this country")
            capital = country.get("capital", ["Unknown"])[0]
            region = country.get("region", "Unknown")
            currency = list(country.get("currencies", {}).keys())[0] if country.get("currencies") else "Unknown"
            language = list(country.get("languages", {}).values())[0] if country.get("languages") else "Unknown"

            quiz_data = [
                {"question": f"What is the capital of {name}?", "answer": capital},
                {"question": f"In which region is {name} located?", "answer": region},
                {"question": f"What is the currency of {name}?", "answer": currency},
                {"question": f"Which language is spoken in {name}?", "answer": language}
            ]

            return random.choice(quiz_data)

        except Exception as e:
            print(f"Error parsing country data: {e}")
            return self._create_fallback_question()

    def _create_fallback_question(self):
        """backup questions if API fails"""
        fallbacks = [
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "Which currency is used in Germany?", "answer": "EUR"},
            {"question": "In which continent is Brazil located?", "answer": "South America"},
            {"question": "What is the official language of Japan?", "answer": "Japanese"},
            {"question": "In which country is the Eiffel Tower located?", "answer": "France"},
            {"question": "Which country is famous for the Great Wall?", "answer": "China"},
            {"question": "Where is the Colosseum located?", "answer": "Italy"},
            {"question": "Which country is home to the Taj Mahal?", "answer": "India"},
            {"question": "Where is Machu Picchu situated?", "answer": "Peru"},
            {"question": "In which country would you find Mount Fuji?", "answer": "Japan"},
            {"question": "Where is the Christ the Redeemer statue located?", "answer": "Brazil"},
            {"question": "Which country is known for tulips and windmills?", "answer": "Netherlands"},
            {"question": "Where is the Kremlin located?", "answer": "Russia"},
            {"question": "Which country hosts the Acropolis of Athens?", "answer": "Greece"},
            {"question": "Where is the Sahara Desert primarily located?", "answer": "Algeria"},
            {"question": "In which country is the Serengeti National Park?", "answer": "Tanzania"},
            {"question": "Which country is famous for the Northern Lights in Reykjavik?", "answer": "Iceland"},
            {"question": "Where is the Neuschwanstein Castle located?", "answer": "Germany"},
            {"question": "Which country has the city of Petra carved into rock?", "answer": "Jordan"},
            {"question": "Where is the city of Dubrovnik, known from Game of Thrones, located?", "answer": "Croatia"},
            {"question": "In which country is the Dead Sea located?", "answer": "Israel"},
            {"question": "Which country is famous for its maple syrup and Niagara Falls?", "answer": "Canada"},
            {"question": "Where is the Sydney Opera House located?", "answer": "Australia"},
            {"question": "Which country is known for the pyramids of Giza?", "answer": "Egypt"},
            {"question": "Where would you find the city of Prague?", "answer": "Czech Republic"},
            {"question": "Which country is home to Table Mountain?", "answer": "South Africa"},
            {"question": "Where is the historic city of Fez located?", "answer": "Morocco"},
            {"question": "In which country is Angkor Wat located?", "answer": "Cambodia"},
            {"question": "Where is the Blue Lagoon geothermal spa located?", "answer": "Iceland"},
            {"question": "Which country is home to Mount Everest?", "answer": "Nepal"},
            {"question": "Where is the Moai statues of Easter Island located?", "answer": "Chile"},
            {"question": "In which country is the Alhambra palace located?", "answer": "Spain"},
            {"question": "Where is the Forbidden City?", "answer": "China"},
            {"question": "Which country is known for its ancient samurai culture?", "answer": "Japan"},
            {"question": "Where is the capital city of Bogotá located?", "answer": "Colombia"},
            {"question": "Which country is home to the city of Istanbul?", "answer": "Turkey"},
            {"question": "Where is the city of Havana located?", "answer": "Cuba"},
            {"question": "Which country is known for its fjords and Vikings?", "answer": "Norway"},
            {"question": "Where is the Louvre Museum located?", "answer": "France"},
            {"question": "In which country is the city of Budapest?", "answer": "Hungary"},
            {"question": "Where is the ancient site of Carthage located?", "answer": "Tunisia"},
            {"question": "Which country is famous for kangaroos and the Outback?", "answer": "Australia"},
            {"question": "Where is the historic city of Lhasa located?", "answer": "China"},
            {"question": "Which country is associated with whisky and bagpipes?", "answer": "Scotland"},
            {"question": "In which country is the Matterhorn mountain?", "answer": "Switzerland"},
            {"question": "Where is the city of Kigali located?", "answer": "Rwanda"},
            {"question": "Which country has the official seat of the European Union?", "answer": "Belgium"},
            {"question": "Where is the historic city of Timbuktu located?", "answer": "Mali"},
            {"question": "Which country is known for samba and Carnival?", "answer": "Brazil"},
            {"question": "Where is the Atacama Desert located?", "answer": "Chile"},
            {"question": "In which country is the Danube Delta?", "answer": "Romania"},
            {"question": "Where is the city of Vientiane located?", "answer": "Laos"},
            {"question": "Which country is famous for Dracula’s Castle?", "answer": "Romania"}
        ]
        return random.choice(fallbacks)


# Uuden Käyttäjän luominen päätepiste
@program.route('/game/users/insert', methods=['POST'])
def insert_new_user():
    try:
        data = request.get_json()

        connection_1 = StarterInformation('localhost', 3306, 'airplane_simulator_v6', 'user', 'password', True)

        # Testataan, jos clientin lähettämä username on jo käytössä, result palauttaa joko True tai False.
        result = connection_1.test_username(data['Username'])

        if result:
            st_airport = connection_1.starting_airport()
            starter_data = {
                'Balance': connection_1.starting_money(),

                'Airport': st_airport,

                'Country': connection_1.starting_country(st_airport),

                'ICAO': connection_1.starting_icao(st_airport),

                'Continent': connection_1.starting_continent(st_airport),

                'Latitude & Longitude': connection_1.starting_lat_lon(st_airport),

                'Visited Countries': 0,

                'Traveled Kilometers': 0,

                'Question': ''
            }

            # Kartta data käyttäjälle 40 satunnaiseen seuraavaan kohteeseen.
            map_data = GenerateTravel('localhost', 3306, 'airplane_simulator_v6', 'user', 'password', True)
            coordinate_list = map_data.list_airports()

            result = connection_1.insert_new_data(data, starter_data)

            if type(result) == str:
                return jsonify({'Error': result})
            else:
                # Kartta data käyttäjälle 40 satunnaiseen seuraavaan kohteeseen.
                map_data = GenerateTravel('localhost', 3306, 'airplane_simulator_v6', 'user', 'password', True)
                coordinate_list = map_data.list_airports()

                # GenerateRealTimeData-class generated data:
                realtimedata = GenerateRealTimeData(starter_data['Latitude & Longitude'][0],
                                                    starter_data['Latitude & Longitude'][1])
                fetchrealtimedata = realtimedata.fetch_real_time_data()

                # Generate the continent quiz:
                quiz_question = CountryQuiz(starter_data['Country']).fetch_country_quiz()

                # Data terminaalissa:
                print("User successfully created!")

                return jsonify({'Airport Data': starter_data,
                                'Personal Data': {'Username': data['Username']},
                                'Map Data': coordinate_list,
                                'Real Time Data': fetchrealtimedata,
                                'Question': ''}, {'Status': 200})

        else:
            return jsonify({'Error': 'Someone already has your cool username, try another.'})

    except Exception as e:
        return jsonify({'Program ran into an error': str(e)}, {'Status': 400})


@program.errorhandler(400)
@program.errorhandler(404)
@program.errorhandler(405)
@program.errorhandler(500)
def errorhandling_super(error):
    if isinstance(error, HTTPException):
        return jsonify({
            'Error-message': error.description,
            'Status': error.code
        }), error.code
    else:
        return jsonify({
            'Error-message': 'Unknown error',
            'Status': 500
        })


# Käyttäjän päivitys päätepiste
@program.route('/game/users/update', methods=['POST'])
def update_user():
    try:
        data = request.get_json()

        # Create a datalist manually in the correct order
        datalist = [
            data['Old Game Data']['Username'],
            data['Old Game Data']['Balance'],
            data['New Game Data']['New Airport'],
            data['New Game Data']['New Country'],
            data['New Game Data']['New ICAO'],
            data['Old Game Data']['ICAO'],
            data['New Game Data']['New Continent'],
            data['New Game Data']['New Latitude'],
            data['New Game Data']['New Longitude'],
            data['Old Game Data']['Visited Countries'],
            data['Old Game Data']['Traveled kilometers']
        ]

        print(datalist)

        connection_1 = UpdateUser('localhost', 3306, 'airplane_simulator_v6', 'user', 'password', True)

        # Update & Insert into datalist
        connection_2 = GenerateTravel('localhost', 3306, 'airplane_simulator_v6', 'user', 'password', True)

        # Increasing traveled kilometers and balance before updating the database:
        traveled_kilometers = connection_2.calculate_distance(datalist[4], datalist[5])
        datalist[10] = int(datalist[10]) + traveled_kilometers

        # Adjusting the country tab to show the full name of the country:
        country_fullname = connection_1.adjust_country(datalist[4])
        datalist[3] = country_fullname

        # Update user data in SQL:
        update_result = connection_1.update(datalist)

        if isinstance(update_result, str):
            return jsonify({'Error': update_result}, {'Status': 400})

        else:
            update_fetch_result = connection_1.fetch_updated_user(datalist[0])

            if isinstance(update_result, str):
                return jsonify({'Error': update_fetch_result}, {'Status': 400})

            else:
                # Kartta data käyttäjälle 40 satunnaiseen seuraavaan kohteeseen.
                map_data = GenerateTravel('localhost', 3306, 'airplane_simulator_v6', 'user', 'password', True)
                coordinate_list = map_data.list_airports()

                # GenerateRealTimeData-class generated data:
                realtimedata = GenerateRealTimeData(update_fetch_result['Latitude'], update_fetch_result['Longitude'])
                fetchrealtimedata = realtimedata.fetch_real_time_data()

                # Generate the continent quiz:
                quiz_question = CountryQuiz(update_fetch_result['Country']).fetch_country_quiz()

                # Data terminaalissa:
                print("User successfully updated!")

                return jsonify({'Personal & Airport Data': update_fetch_result,
                                'Map Data': coordinate_list,
                                'Real Time Data': fetchrealtimedata,
                                'Question': quiz_question}, {'Status': 200})

    except Exception as e:
        return jsonify({'Program ran into an error': str(e)}, {'Status': 400})


@program.errorhandler(400)
@program.errorhandler(404)
@program.errorhandler(405)
@program.errorhandler(500)
def errorhandling_super(error):
    if isinstance(error, HTTPException):
        return jsonify({
            'Error-message': error.description,
            'Status': error.code
        }), error.code
    else:
        return jsonify({
            'Error-message': 'Unknown error',
            'Status': 500
        })


# Pelin lataaminen päätepiste
@program.route('/game/users/load', methods=['POST'])
def load_game():
    try:
        data = request.get_json()

        connection_1 = LoadGame('localhost', 3306, 'airplane_simulator_v6', 'user', 'password', True)

        # Testataan, jos clientin lähettämä käyttäjätunnus ja salasana löytyvät, result palauttaa joko True tai False, ja jatko on sen mukainen.
        result = connection_1.test_user_name_password(data['Username'], data['Password'])

        if result:
            userdata = connection_1.load_save(data['Username'])

            if type(userdata) == str:
                return jsonify({'Error': userdata})
            else:

                # GenerateTravel-class generated data:
                map_data = GenerateTravel('localhost', 3306, 'airplane_simulator_v6', 'user', 'password', True)
                map_coordinates = map_data.list_airports()

                # GenerateRealTimeData-class generated data:
                real_time = GenerateRealTimeData(userdata['Latitude'], userdata['Longitude'])
                real_time_data = real_time.fetch_real_time_data()

                # Data terminaalissa:
                print("User successfully loaded!")

                return jsonify({'Loaded Personal Data': userdata,
                                'Map Data': map_coordinates,
                                'Real Time Data': real_time_data}, {'Status': 200})

        elif result == False:
            return jsonify({'Error Message': 'Either the password or/and the username given were wrong.'})

        else:
            return jsonify({'Error': result})

    except Exception as e:
        return jsonify({'Program ran into an error': str(e)}, {'Status': 400})


@program.errorhandler(400)
@program.errorhandler(404)
@program.errorhandler(405)
@program.errorhandler(500)
def errorhandling_super(error):
    if isinstance(error, HTTPException):
        return jsonify({
            'Error-message': error.description,
            'Status': error.code
        }), error.code
    else:
        return jsonify({
            'Error-message': 'Unknown error',
            'Status': 500
        })


# Käyttäjän vapaavalintainen poistaminen päätepiste
@program.route('/game/users/delete', methods=['POST'])
def delete_user():
    try:
        data = request.get_json()

        connection = Utility('localhost', 3306, 'airplane_simulator_v6', 'user', 'password', True)

        result = connection.delete_user(data['Username'])

        if type(result) == str:
            return jsonify({'Error': result}, {'Status': 400})

        elif result == True:
            return jsonify({'Message': f"Käyttäjäsi {data['Username']} on poistettu onnistuneesti."})

        else:
            return jsonify({'Message': f"Käyttäjäsi {data['Username']} poistamisessa ilmeni odottamaton virhe."})

    except Exception as e:
        return jsonify({'Error-message': str(e)}, {'Status': 400})


@program.errorhandler(400)
@program.errorhandler(404)
@program.errorhandler(405)
@program.errorhandler(500)
def errorhandling_super(error):
    if isinstance(error, HTTPException):
        return jsonify({
            'Error-message': error.description,
            'Status': error.code
        }), error.code
    else:
        return jsonify({
            'Error-message': 'Unknown error',
            'Status': 500
        })


# Palautteen päätepiste
@program.route('/game/send/feedback', methods=['POST'])
def feedback():
    try:
        data = request.get_json()
        print(f'Retrieved data: {data}')

        # Ei haeta enää nicknameä tietokannasta, vaan otetaan suoraan lomakkeelta
        nickname = data.get("nickname", "Unknown")

        datalist = [
            data.get("firstName", ""),
            data.get("lastName", ""),
            nickname,
            data.get("email", ""),
            "N/A",  # phone_number
            "N/A",  # country
            data.get("feedback", "")
        ]

        connection_1 = Utility('localhost', 3306, 'airplane_simulator_v6', 'user', 'password', True)
        result = connection_1.send_feedback(datalist)

        print(f"DEBUG DATALIST: {datalist}")

        if isinstance(result, str):
            return jsonify({'Error-message': result, 'Status': 400})
        else:
            if result:
                return jsonify({'Message': 'Feedback successfully sent.', 'Status': 200})
            else:
                return jsonify({'Message': 'Feedback was not sent successfully, please try again.', 'Status': 500})


    except Exception as e:
        return jsonify({'Program ran into an error': str(e), 'Status': 400})


@program.errorhandler(400)
@program.errorhandler(404)
@program.errorhandler(405)
@program.errorhandler(500)
def errorhandling_super(error):
    if isinstance(error, HTTPException):
        return jsonify({
            'Error-message': error.description,
            'Status': error.code
        }), error.code
    else:
        return jsonify({
            'Error-message': 'Unknown error',
            'Status': 500
        })


# Leaderboards päätepiste
@program.route('/game/users/leaderboards', methods=['GET'])
def show_leaderboards():
    try:
        connection = Utility('localhost', 3306, 'airplane_simulator_v6', 'user', 'password', True)
        leaderboard_data = connection.show_leaderboard()

        # Handle error cases where string is returned
        if isinstance(leaderboard_data, str):
            return jsonify({
                'Error': leaderboard_data,
                'Status': 404
            }), 404

        # Format the data properly
        formatted_data = [
            {
                'username': row[0],  # nick
                'balance': row[1],  # balance
                'rank': idx + 1  # add ranking
            }
            for idx, row in enumerate(leaderboard_data)
        ]

        return jsonify({
            'Leaderboard': formatted_data,
            'Status': 200
        })

    except Exception as e:
        return jsonify({
            'Error': str(e),
            'Status': 500
        }), 500


@program.errorhandler(400)
@program.errorhandler(404)
@program.errorhandler(405)
@program.errorhandler(500)
def errorhandling_super(error):
    if isinstance(error, HTTPException):
        return jsonify({
            'Error-message': error.description,
            'Status': error.code
        }), error.code
    else:
        return jsonify({
            'Error-message': 'Unknown error',
            'Status': 500
        })


# Save & Quit päätepiste
@program.route('/game/users/savenquit', methods=['POST'])
def save_n_quit():
    try:
        data = request.get_json()

        # Create a datalist manually in the correct order
        datalist = [
            data['Old Game Data']['Username'],
            data['Old Game Data']['Balance'],
            data['New Game Data']['New Airport'],
            data['New Game Data']['New Country'],
            data['New Game Data']['New ICAO'],
            data['Old Game Data']['ICAO'],
            data['New Game Data']['New Continent'],
            data['New Game Data']['New Latitude'],
            data['New Game Data']['New Longitude'],
            data['Old Game Data']['Visited Countries'],
            data['Old Game Data']['Traveled kilometers']
        ]

        connection_1 = UpdateUser('localhost', 3306, 'airplane_simulator_v6', 'user', 'password', True)

        # Update user data in SQL:
        update_result = connection_1.update(datalist)
        if isinstance(update_result, str):
            return jsonify({'Error': update_result}, {'Status': 400})

        else:
            update_fetch_result = connection_1.fetch_updated_user(datalist[0])

            if isinstance(update_fetch_result, str):
                return jsonify({'Error': update_fetch_result}, {'Status': 400})

            else:
                return jsonify({'Saved Data': update_fetch_result,
                                'Exit-Message': 'Data successfully updated'}, {'Status': 200})

    except Exception as e:
        return jsonify({'Program ran into an error': str(e)}, {'Status': 400})


@program.errorhandler(400)
@program.errorhandler(404)
@program.errorhandler(405)
@program.errorhandler(500)
def errorhandling_super(error):
    if isinstance(error, HTTPException):
        return jsonify({
            'Error-message': error.description,
            'Status': error.code
        }), error.code
    else:
        return jsonify({
            'Error-message': 'Unknown error',
            'Status': 500
        })


if __name__ == '__main__':
    program.run(use_reloader=True, host='127.0.0.1', port=5000)
