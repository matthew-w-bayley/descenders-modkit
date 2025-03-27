""" Used to host the website using flask """
import os
import asyncio


# Flask imports
from quart import (
    Quart,
    request,
    jsonify,
    send_file
)
from quart_cors import cors
from common.dbms import DBMS

webserver_app = Quart(__name__)

class WebserverRoute():
    """ Used to denote a webserver url to view function """
    def __init__(self, route, endpoint, view_func, methods):
        self.route = route
        self.endpoint = endpoint
        self.view_func = view_func
        self.methods = methods

    def is_valid(self):
        """ Function to check if the route is valid """
        return (
            self.route is not None
            and self.endpoint is not None
            and self.view_func is not None
            and self.methods is not None
        )

    def to_dict(self):
        """ Function to convert the route to a dictionary """
        return {
            "route": self.route,
            "endpoint": self.endpoint,
            "view_func": self.view_func,
            "methods": self.methods
        }

class Webserver():
    """ Used to host the website using flask """
    def __init__(self, dbms : DBMS):
        self.dbms = dbms
        self.webserver_app = webserver_app
        self.webserver_app = cors(self.webserver_app)
        self.routes = [
            WebserverRoute(
                "/get-leaderboard", "get_leaderboard",
                self.get_leaderboard_for_trail, ["GET"]
            ),
            WebserverRoute(
                "/get-all-times", "get_all_times",
                self.get_all_times, ["GET"]
            ),
            WebserverRoute(
                "/get-trails", "get_trails",
                self.get_trails, ["GET"]
            ),
            WebserverRoute(
                '/upload-replay',
                'upload_replay',
                self.upload_replay,
                ['POST']
            ),
            WebserverRoute(
                '/download-replay/<time_id>',
                'get_replay',
                self.get_replay,
                ['GET']
            ),
            WebserverRoute(
                '/trails/<trail_csv>',
                'get_trail_csv',
                self.get_trail_csv,
                ['GET']
            ),
            WebserverRoute(
                '/get-total-stored-times',
                'get_total_stored_times',
                self.get_total_stored_times,
                ['GET']
            ),
            WebserverRoute(
                '/get-gb-stored-replays',
                'get_gb_stored_replays',
                self.get_gb_stored_replays,
                ['GET']
            ),
        ]
        self.tokens_and_ids = {}
        import asyncio
        asyncio.run(self.add_routes())

    async def add_routes(self):
        """ Adds the routes to the flask app """
        for route in self.routes:
            self.webserver_app.add_url_rule(
                route.route,
                    endpoint=route.endpoint,
                view_func=route.view_func,
                methods=route.methods
            )

    async def get_trail_csv(self, trail_csv):
        """ Function to get the trail csv """
        try:
            return await send_file(f"trails/{trail_csv}")
        except FileNotFoundError:
            return "No trail found!"

    async def upload_replay(self):
        """ Function to upload a replay to the server """
        files = await request.files
        form = await request.form
        replay = files["replay"]
        time_id = form.get("time_id")
        if replay.filename == "":
            return "No selected file"
        await replay.save(f"replays/{time_id}.replay")
        return "Replay uploaded successfully!"

    async def get_gb_stored_replays(self):
        """Get the file size of replays in GB """
        if not os.path.exists("replays"):
            return "0.0"
        return str(round(sum(
            os.path.getsize(f"replays/{f}")
            for f in os.listdir("replays")
        ) / 1_000_000_000, 2))
    
    async def get_total_stored_times(self):
        """Get the total number of stored times"""
        # extract timestamp
        timestamp = request.args.get("timestamp")
        try:
            if timestamp is not None:
                return str(await self.dbms.get_total_stored_times(int(round(float(timestamp)))))
            return str(await self.dbms.get_total_stored_times())
        except asyncio.exceptions.CancelledError:
            return jsonify({})

    async def get_replay(self, time_id):
        """ Function to get the replay of a time with id time_id """
        time_id = time_id.split(".")[0]
        try:
            return await send_file("replays/" + time_id + ".replay", as_attachment = True, attachment_filename=f"{time_id}.replay")
        except FileNotFoundError:
            return "No replay found!"

    async def get_trails(self):
        """ Function to get the trails """ 
        return jsonify({"trails": (await self.dbms.get_trails())})

    async def get_leaderboard_for_trail(self):
        """ Function to get the leaderboard of the website"""

        trail_name = request.args.get("trail_name")
        world_name = request.args.get("world_name")
        if trail_name is None or world_name is None:
            return jsonify({})

        try:
            leaderboard = await self.dbms.get_leaderboard(trail_name, world_name)
        except asyncio.exceptions.CancelledError:
            return jsonify({})
        return jsonify([
                {
                    "place": player_time["place"],
                    "starting_speed": player_time["starting_speed"],
                    "name": player_time["name"],
                    "bike": player_time["bike"],
                    "version": player_time["version"],
                    "verified": player_time["verified"],
                    "deleted": player_time["deleted"],
                    "time_id": str(player_time["time_id"]),
                    "time": player_time["time"],
                    "submission_timestamp": player_time["submission_timestamp"],
                }
                for player_time in leaderboard
            ])

    async def get_all_times(self):
        """ Function to get all the times of the website"""
        page = int(request.args.get("page"))
        items_per_page = int(request.args.get("items_per_page"))
        sort_by = request.args.get("sort_by")
        order = request.args.get("order")
        search = request.args.get("search")
        times = await self.dbms.get_recent_times(
            page, items_per_page, sort_by, order == "desc", search
        )
        return jsonify(
            {
                "times": times[0],
                "num_times": times[1]
            }
        )
