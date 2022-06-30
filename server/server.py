import tornado.ioloop
import tornado.web
import tornado.gen
from string import Template
from query_gbq import init_client, init_dataset, execute_query

# Heroku gives us the port to listen on
import os

port = int(os.getenv("PORT", 8888))

# Dict mapping query_type to the file containing the queries
query_types = {
    "packages_today": "server/queries/packages_today.sql",
    "package_info": "server/queries/package_info.sql",
}


class QueryHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        # Allow CORS
        # TODO: restrict origin?
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def load_template(self, path, **kwargs):
        with open(path, "r") as file:
            template = Template(file.read())
            return template.substitute(**kwargs)

    @tornado.gen.coroutine
    def get(self):
        query_type = self.get_argument("query_type")
        if query_type not in query_types.keys():
            self.write("Invalid query")
            return
        if query_type == "package_info":
            package_name = self.get_argument("package_name")
            query = self.load_template(
                query_types["package_info"], projectname=package_name
            )
        else:
            # packages_today
            query = self.load_template(query_types["packages_today"])
        df = execute_query(query)
        self.write(df.to_json())
        self.finish()


def make_app():
    return tornado.web.Application([(r"/query", QueryHandler)])


init_client()
init_dataset()
app = make_app()
app.listen(port)
tornado.ioloop.IOLoop.current().start()
