using System;
using System.Collections;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using UnityEngine.Networking;
using System.IO;
using System.Security.Cryptography;

namespace ModLoaderSolution
{
	public enum DebugType
    {
		DEVELOPER, DEBUG, RELEASE
    }
	public class NetClient : MonoBehaviour {
		public static NetClient Instance { get; private set; }
		public RidersGate[] ridersGates;
		private TcpClient socketConnection;
		float hasStarted = Time.time;
		private Thread clientReceiveThread;
		bool PlayerCollision = false;
		List<string> messages = new List<string>();
		public int port = 65433;
		public string ip = "86.26.185.112";
		static string version = "0.4.05";
		static bool quietUpdate = false;
		static string patchNotes = "This version contains a hotfix for replays failing to upload. Some previous times may not be verifiable due to this error. Hopefully this bug is resolved.\n\n\nYours,\n- nohumanman"; // that which has changed since the last version.
		public static DebugType debugState = DebugType.RELEASE;
        [System.Diagnostics.CodeAnalysis.SuppressMessage("CodeAnalysis", "IDE0051:Unused member", Justification = "Called by Unity DI")]
        void Awake(){
			using (new MethodAnalysis())
			{
                if (debugState == DebugType.DEVELOPER)
                    ip = "localhost";
                DontDestroyOnLoad(this.gameObject.transform.root);
                if (Instance != null && Instance != this)
                    Destroy(this);
                else
                    Instance = this;
                this.gameObject.AddComponent<Utilities>();
                Utilities.Log("Version number " + version);
                Application.logMessageReceived += Log;
            }
		}
		public static string GetVersion()
        {
			if (debugState == DebugType.DEVELOPER)
				return version + "-dev";
			else if (debugState == DebugType.DEBUG)
				return version + "-debug";
			else
				return version;
        }
		[System.Diagnostics.CodeAnalysis.SuppressMessage("CodeAnalysis", "IDE0051:Unused member", Justification = "Called by Unity DI")]
		void Start()
		{
			using (new MethodAnalysis())
			{
				Utilities.Log("Connecting to tcp server port " + port.ToString() + " with ip '" + ip + "'");
				ConnectToTcpServer();
				ridersGates = FindObjectsOfType<RidersGate>();
				if (new PlayerIdentification.SteamIntegration().getName() == "Descender")
				{
					Utilities.instance.ToggleGod();
				}
			}
		}
		public bool IsConnected()
        {
			return socketConnection != null && socketConnection.Connected;
		}
		bool poppedUp = false;
        [System.Diagnostics.CodeAnalysis.SuppressMessage("CodeAnalysis", "IDE0051:Unused member", Justification = "Called by Unity DI")]
        void Update()
        {
			if (!poppedUp && Utilities.GetPlayer() != null)
            {
				string lastVersion = "";
				try
				{
					lastVersion = File.ReadAllText(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData) + "Low\\RageSquid\\Descenders\\last_version.txt");
				}
				catch(Exception){
				}
				if (lastVersion != NetClient.version && !quietUpdate)
                {
					try
					{
						Utilities.instance.PopUp("Modkit patch notes " + NetClient.version, NetClient.patchNotes);
						poppedUp = true;
					}
					catch (Exception) { }
				}
				File.WriteAllText(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData) + "Low\\RageSquid\\Descenders\\last_version.txt", NetClient.version);
			}
			if (Input.GetKey(KeyCode.LeftShift) && Input.GetKeyDown(KeyCode.P)) {
                string path = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData) + "Low\\RageSquid\\Descenders\\method-calls.csv";
                HolisticMethodAnalysis.WriteCalledMethodsToCsv(path);
            }
				
			if (Input.GetKey(KeyCode.LeftShift) && Input.GetKeyDown(KeyCode.C))
            {
				UserInterface.Instance.SpecialNotif("Collisions enabled: " + (!PlayerCollision).ToString());
				Physics.IgnoreLayerCollision(8, 8, PlayerCollision);
				PlayerCollision = !PlayerCollision;
			}
			if (Time.time - hasStarted > 10 && (socketConnection == null || !socketConnection.Connected))
            {
				Utilities.Log("Disconnected! Reconnecting now...");
                // SplitTimerText.Instance.count = false;
                SplitTimerText.Instance.text.color = Color.red;
				SplitTimerText.Instance.checkpointTime = "";
				ConnectToTcpServer();
            }
            try
            {
				foreach (string message in messages)
				{
					try
					{
						MessageRecieved(message);
						messages.Remove(message);
					}
					catch (Exception){ }
				}
				messages.Clear();
			}
			catch (InvalidOperationException){}
		}
		private void ConnectToTcpServer () {
			Utilities.LogMethodCallStart();
			Utilities.Log("Connecting to TCP Server");
			hasStarted = Time.time;
			try {
				clientReceiveThread = new Thread (new ThreadStart(ListenForData));
				clientReceiveThread.IsBackground = true;
				clientReceiveThread.Start();
				hasStarted = Time.time;
			}
			catch (Exception e) {
				Utilities.Log("On client connect exception " + e); 		
			}
			Utilities.LogMethodCallEnd();
		}
		public void Log(string logString, string stackTrace, LogType type)
		{
			//SendData("LOG_LINE", logString);
		}
		public void Log(string logString)
        {
			//SendData("LOG_LINE", logString);
        }
		public IEnumerator UploadOutputLog()
		{
			Utilities.LogMethodCallStart();
			string replayLocation = (
				Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData)
				+ "Low\\RageSquid\\Descenders\\output_log.txt"
			);
			Byte[] bytes = System.IO.File.ReadAllBytes(replayLocation);

			WWWForm form = new WWWForm();
			form.AddField("player_id", new PlayerIdentification.SteamIntegration().getSteamId());
			form.AddBinaryData("replay", bytes, "replay");

			using (UnityWebRequest www = UnityWebRequest.Post(
				"https://modkit.nohumanman.com/upload-outputlog",
				form
			))
			{
				yield return www.SendWebRequest();

				if (www.isNetworkError || www.isHttpError)
				{
					Utilities.Log(www.error);
				}
				else
				{
					Utilities.Log("Upload complete!");
				}
			}
			Utilities.LogMethodCallEnd();
		}
		public void UploadReplay(string replay, string time_id)
		{
			Byte[] bytes = System.IO.File.ReadAllBytes(replay);
			if (bytes.Length < 10)
			{
				Utilities.instance.PopUp("Replay failed to upload!", "Time will be invalidated...");
				return;
			}
			string base64Replay = Convert.ToBase64String(bytes);

			string message = $"UPLOAD_REPLAY|{time_id}|{base64Replay}\n";
			_SendData(message);
		}
        private void ListenForData()
        {
            try
            {
                Utilities.Log("Creating TcpClient()");
                socketConnection = new TcpClient(ip, port);
                Utilities.Log("TcpClient created!");
                Byte[] bytes = new Byte[1024];
                StringBuilder dataBuffer = new StringBuilder();

                using (NetworkStream stream = socketConnection.GetStream())
                {
                    int length;
                    while ((length = stream.Read(bytes, 0, bytes.Length)) != 0)
                    {
                        string receivedData = Encoding.ASCII.GetString(bytes, 0, length);
                        dataBuffer.Append(receivedData);

                        // Process complete messages
                        while (true)
                        {
                            int newlineIndex = dataBuffer.ToString().IndexOf('\n');
                            if (newlineIndex == -1)
                                break; // No complete message yet, wait for more data

                            string completeMessage = dataBuffer.ToString(0, newlineIndex);
                            messages.Add(completeMessage);

                            // Remove processed message from buffer
                            dataBuffer.Remove(0, newlineIndex + 1);
                        }
                    }
                }
            }
            catch
            {
                Utilities.Log("Socket exception in ListenForData()");
            }
        }

        public void NetStart()
        {
			Utilities.LogMethodCallStart();
			PlayerManagement.Instance.NetStart();
			this.SendData("REP", Utilities.instance.GetPlayerTotalRep());
			foreach (Boundary b in FindObjectsOfType<Boundary>())
				b.ForceUpdate(); // force tell the server what boundaries we are in.
            Timer timer = new Timer(SendHeartbeat, null, 0, 5000);  // Sends heartbeat every 5 seconds
            Utilities.LogMethodCallEnd();
		}
		private void MessageRecieved(string message) {
			Utilities.LogMethodCallStart();
			if (message == "")
				return;
			Utilities.Log("Message Recieved: " + message);
			if (message == "SUCCESS") {
				NetStart();
			}
			if (message.StartsWith("ROTATE|"))
            {
				string rotate = message.Split('|')[1];
				int rotateInt = int.Parse(rotate);
				Utilities.GetPlayer().transform.Rotate(new Vector3(0, rotateInt, 0));
			}
			if (message.StartsWith("UPLOAD_REPLAY"))
            {
				string time_id = message.Split('|')[1];

				string replayLocation = (
					Application.persistentDataPath + "/Replays/"
					 + time_id + ".replay"
                );
				if (!File.Exists(replayLocation)){
                    // if replay doesn't exist then save it
                    Utilities.instance.SaveReplayToFile(time_id);
					if (!File.Exists(replayLocation))
					{
						// critical error
						Utilities.instance.PopUp("Critical Error", "Replay failed to save, please report this in the Descenders Competitive server with your output-log.txt!");
						SendData("LOG_TO_PRINT", "Critical Error, replay failed to save in '" + replayLocation + "'");
					}
                }
				// upload replay
                UploadReplay(replayLocation, time_id);
			}
			if (message.StartsWith("GET_POS"))
            {
				Vector3 pos = Utilities.GetPlayer().transform.position;
				Utilities.Log("Current Position: " + pos.ToString());
				SendData("POS", pos.x, pos.y, pos.z);
            }
			if (message.StartsWith("SET_TEXT_COLOUR"))
            {
				string r = message.Split('|')[1];
				string b = message.Split('|')[2];
				string g = message.Split('|')[3];
				SplitTimerText.Instance.text.color = new Color(
					int.Parse(r),
					int.Parse(b),
					int.Parse(g)
				);
			}
			if (message.StartsWith("SET_TEXT_COL_DEFAULT"))
				SplitTimerText.Instance.TextColToDefault();
			if (message == "PRIVATE_LOBBY")
            {
				//Utilities.instance.GoToPrivateLobby();
			}
			if (message.StartsWith("SPEEDRUN_DOT_COM_LEADERBOARD"))
			{
				string[] leaderboard = message.Split('|');
				string trailName = leaderboard[1];
				foreach (Trail trail in GameObject.FindObjectsOfType<Trail>())
				{
					if (trail.name == trailName)
					{
						string leaderboardJson = leaderboard[2];
						Debug.Log("Speedrun.com:" + leaderboardJson);
						LeaderboardInfo leaderboardInfo = JsonUtility.FromJson<LeaderboardInfo>(leaderboardJson.Replace("'", "\""));
						trail.leaderboardText.GetComponent<TextMesh>().text = trailName + " (from speedrun.com)\n" + leaderboardInfo.LeaderboardAsString();
					}
				}
			}
			if (message.StartsWith("LEADERBOARD"))
			{
				string[] leaderboard = message.Split('|');
				string trailName = leaderboard[1];
				foreach (Trail trail in GameObject.FindObjectsOfType<Trail>())
				{
					if (trail.name == trailName)
					{
						string leaderboardJson = leaderboard[2];
						Debug.Log(leaderboardJson);
						LeaderboardInfo leaderboardInfo = JsonUtility.FromJson<LeaderboardInfo>(leaderboardJson.Replace("'", "\""));
						trail.autoLeaderboardText.GetComponent<TextMesh>().text = trailName + "\n" + leaderboardInfo.LeaderboardAsString();
					}
				}
			}
			if (message.StartsWith("TIMER_FINISH"))
			{
				string[] leaderboard = message.Split('|');
				string info = leaderboard[1];
				SplitTimerText.Instance.count = false;
				SplitTimerText.Instance.text.color = Color.green;
				SplitTimerText.Instance.SetText(info);
			}
			if (message.StartsWith("BAIL"))
            {
				GetComponent<Utilities>().Bail();
            }
			if (message.StartsWith("BANNED")) {
				string[] ban = message.Split('|');
				string method = ban[1];
				if (method == "CRASH")
					while (true) { }
				if (method == "CLOSE")
					Application.Quit();
			}
			if (message.StartsWith("SET_BIKE_SIZE"))
            {
				string[] ban = message.Split('|');
				float playerSize = float.Parse(ban[1]);
				GetComponent<ModLoaderSolution.Utilities>().SetPlayerSize(playerSize);
			}
			if (message.StartsWith("RIDERSGATE")) {
				string[] gate = message.Split('|');
				float randomTime = float.Parse(gate[1]);
				foreach (RidersGate ridersGate in ridersGates)
					if (!Utilities.instance.isInPauseMenu()) // not in pause menu
						ridersGate.TriggerGate(randomTime);
			}
			if (message.StartsWith("LOG_GAMEOBJECTS"))
			{
				foreach (GameObject go in FindObjectsOfType<GameObject>())
					Utilities.Log(go);
			}
			if (message.StartsWith("TOGGLE_SPECTATOR"))
            {
				GetComponent<Utilities>().ToggleSpectator();
			}
			if (message.StartsWith("SPECTATE"))
            {
				string id = message.Split('|')[1];
                // tell the server that we're spectating this id
                Debug.Log("Telling server we're spectating them");
                NetClient.Instance.SendData("SPECTATE", id);
                Utilities.instance.SpectatePlayerCustom(id);
            }
			if (message.StartsWith("SET_BIKE"))
            {
				string new_bike = message.Split('|')[1];
				string steam_id;
				try { steam_id = message.Split('|')[2]; }
                catch{ steam_id = (new PlayerIdentification.SteamIntegration().id).ToString(); }
				FindObjectOfType<BikeSwitcher>().ToBike(new_bike, steam_id);
			}
			if (message.StartsWith("GET_IDS"))
            {
				foreach (global::PlayerInfo inf in Singleton<PlayerManager>.SP.GetAllPlayers())
                    Utilities.Log(Utilities.FromPlayerInfo(inf).steamID);
			}
			if (message.StartsWith("FREEZE_PLAYER"))
            {
				Utilities.instance.FreezePlayer();
			}
			if (message.StartsWith("POPUP"))
			{
				string title = message.Split('|')[1];
				string body = message.Split('|')[2];
				Utilities.instance.PopUp(title, body);
			}
			if (message.StartsWith("TOGGLE_CONTROL"))
            {
				string shouldStr = message.Split('|')[1];
				bool should = shouldStr == "true";
				Utilities.instance.ToggleControl(should);
			}
			if (message.StartsWith("CLEAR_SESSION_MARKER"))
            {
				Utilities.instance.ClearSessionMarker();
			}
			if (message.StartsWith("RESET_PLAYER"))
            {
				Utilities.instance.ResetPlayer();
			}
			if (message.StartsWith("ADD_MODIFIER"))
            {
				string modifier = message.Split('|')[1];
				Utilities.instance.AddGameModifier(modifier);
			}
			if (message.StartsWith("NON_MODKIT_TRAIL"))
            {
				string url = message.Split('|')[1];
				bool proceed = true;
				foreach (Trail trail in FindObjectsOfType<Trail>())
					if (trail.url == url)
						proceed = false;
				if (proceed)
                {
					GameObject trailParent = new GameObject();
					Trail tr = trailParent.AddComponent<Trail>();
					tr.LoadFromUrl("https://modkit.nohumanman.com/api/trails/" + url);
				}
			}
			if (message.StartsWith("SPLIT_TIME"))
            {
				string splitTime = message.Split('|')[1];
				SplitTimerText.Instance.CheckpointTime(splitTime);
			}
			if (message.StartsWith("RESPAWN_ON_TRACK"))
            {
				Utilities.instance.RespawnOnTrack();
			}
			if (message.StartsWith("RESPAWN_AT_START"))
            {
				Utilities.instance.RespawnAtStartline();
			}
			if (message.StartsWith("SET_FAR_CLIP"))
            {
				CameraModifier.Instance.farClipPlane = float.Parse(message.Split('|')[1]);
			}
			if (message.StartsWith("INVALIDATE_TIME"))
            {
				string[] gate = message.Split('|');
				string reason = gate[1];
				SplitTimerText.Instance.count = false;
				SplitTimerText.Instance.SetText(reason);
				SplitTimerText.Instance.text.color = Color.red;
				StopCoroutine("DisableTimerText");
				StartCoroutine(SplitTimerText.Instance.DisableTimerText(5));
			}
			if (message.StartsWith("CUT_BRAKES"))
            {
				GetComponent<Utilities>().CutBrakes();
			}
			if (message.StartsWith("TOGGLE_COLLISION"))
            {
				Physics.IgnoreLayerCollision(8, 8, PlayerCollision);
				PlayerCollision = !PlayerCollision;
			}
			if (message.StartsWith("SET_VEL"))
            {
				string[] gate = message.Split('|');
				string multiplicationFactor = gate[1];
				GetComponent<Utilities>().SetVel(
					float.Parse(multiplicationFactor)
				);
			}
			if (message.StartsWith("GRAVITY"))
            {
				string[] gate = message.Split('|');
				GetComponent<Utilities>().Gravity(float.Parse(gate[1]));
			}
			if (message.StartsWith("SET_REP"))
            {
				string[] gate = message.Split('|');
				Utilities.instance.SetRep(int.Parse(gate[1]));
            }
			if (message.StartsWith("GET_REP"))
            {
				this.SendData("REP", Utilities.instance.GetPlayerTotalRep());
			}
			if (message.StartsWith("SEND_OUTPUTLOG"))
            {
				StartCoroutine(UploadOutputLog());
            }
			if (message.StartsWith("MODIFY_SPEED"))
            {
				if (gameObject.GetComponent<TimeModifier>() == null)
					gameObject.AddComponent<TimeModifier>();
				TimeModifier timeModifier = gameObject.GetComponent<TimeModifier>();
				timeModifier.speed = float.Parse(message.Split('|')[1]);
			}
			if (message.StartsWith("ENABLE_STATS"))
            {
				Utilities.instance.EnableStats();
			}
			if (message.StartsWith("TOGGLE_GOD"))
            {
				Utilities.instance.ToggleGod();
			}
			if (message.StartsWith("UNLOCK_ITEM"))
            {
				string code = message.Split('|')[1];
				CustomizationItem itemFromID = Singleton<CustomizationManager>.SP.GetItemFromID(int.Parse(code));
				Singleton<CustomizationManager>.SP.UnlockItem(itemFromID, addToNewlyUnlocked: true, silent: false);
			}
			if (message.StartsWith("LOCK_ITEM"))
			{
				string code = message.Split('|')[1];
				DevCommandsGameplay.LockItem(int.Parse(code));
			}
			Utilities.LogMethodCallEnd();
		}
        void SendHeartbeat(object state)
        {
            SendData("HEARTBEAT");
        }
		public string clean(string mess)
        {
			foreach (char c in mess)
			{
				if (c < 32 || c > 126)
					mess = mess.Replace(c.ToString(), "?");
			}
			return mess;
		}
        public void SendData(params object[] data)
        {
			string clientMessage = "";
			foreach (object arg in data) 
				clientMessage += clean(arg.ToString()) + "|";
            _SendData(clientMessage);
        }
		void _SendData(string clientMessage) {
			if (!clientMessage.EndsWith("\n"))
				clientMessage = clientMessage + "\n";
            try
            {
                NetworkStream stream = socketConnection.GetStream();
                if (stream.CanWrite)
                {
                    byte[] clientMessageAsByteArray = Encoding.ASCII.GetBytes(clientMessage);
                    stream.Write(clientMessageAsByteArray, 0, clientMessageAsByteArray.Length);
                    stream.Flush(); // Ensure data is flushed immediately
                }
            }
            catch (SocketException socketException)
            {
                Utilities.Log("Socket exception: " + socketException);
            }
		}
        public void OnDestroy()
		{
			SendData("MAP_EXIT");
			if (socketConnection != null)
				socketConnection.Close();
			Application.logMessageReceived -= Log;
		}
	}
}
