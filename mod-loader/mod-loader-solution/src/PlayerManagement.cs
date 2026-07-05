using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using PlayerIdentification;
using ModLoaderSolution;
using UnityEngine.SceneManagement;
using System;
using ConsoleUtils;

namespace ModLoaderSolution
{
	public class PlayerManagement : MonoBehaviour {
		SteamIntegration steamIntegration = new SteamIntegration();
		GameObject PlayerHuman;
		Vector3 PreviousPos = Vector3.zero;
		public float speed;
		bool wasBailed = false;
		public static PlayerManagement Instance { get; private set; }
        [System.Diagnostics.CodeAnalysis.SuppressMessage("CodeAnalysis", "IDE0051:Unused member", Justification = "Called by Unity DI")]
        void Awake(){
			Utilities.Log("LocalApplicationData '" + Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData) + "'");
			Utilities.Log("Version number " + NetClient.GetVersion());
			if (Instance != null && Instance != this) 
				Destroy(this); 
			else
				Instance = this; 
		}
        [System.Diagnostics.CodeAnalysis.SuppressMessage("CodeAnalysis", "IDE0051:Unused member", Justification = "Called by Unity DI")]
		void Update()
		{
		    // Safety check for Utilities
		    if (Utilities.instance == null) return;
		
		    string currentMap = Utilities.instance.GetCurrentMap();
		    
		    // Check if map changed, but also check if NetClient is ready
		    if (currentMap != prevMap)
		    {
		        OnMapEnter(currentMap);
		    }
		
		    if (PlayerHuman == null)
		        PlayerHuman = Utilities.GetPlayer();
		
		    if (Utilities.instance.hasBailed() && !wasBailed)
		        OnRespawn();
		        
		    wasBailed = Utilities.instance.hasBailed();
		
		    if (PlayerHuman != null)
		        CheckForRespawn();
		}
        public void NetStart(){
			OnMapEnter(Utilities.instance.GetCurrentMap());
            OnBikeSwitch(BikeSwitcher.GetBike());
			NetClient.Instance.SendData("VERSION", NetClient.GetVersion());
			NetClient.Instance.SendData("STEAM_ID", steamIntegration.getSteamId());
			NetClient.Instance.SendData("STEAM_NAME", steamIntegration.getName());
			foreach (Trail trail in FindObjectsOfType<Trail>())
            {
				Utilities.Log("Looking for leaderboard texts on trail '" + trail.name + "'");
				//trail.leaderboardText.GetComponent<TextMesh>().font = AssetBundling.Instance.bundle.LoadAsset<UnityEngine.UI.Text>("");
				if (trail.leaderboardText != null)
                {
					Utilities.Log("Found Speedrun.com Leaderboard for '" + trail.name + "'");
					NetClient.Instance.SendData("SPEEDRUN_DOT_COM_LEADERBOARD", trail.name);
				}
				if (trail.autoLeaderboardText != null)
                {
					Utilities.Log("Found auto Leaderboard for '" + trail.name + "'");
					NetClient.Instance.SendData("LEADERBOARD", trail.name);
				}
            }
		}
		string prevMap = "";
		public void CheckForRespawn()
		{
            // if player doesn't exist they can't respawn
            if (Utilities.GetPlayer() == null) return;
			// if human has moved very quickly then they have respawned
            if (Vector3.Distance(PlayerHuman.transform.position, PreviousPos) > 6)
            {
                OnRespawn();
                PreviousPos = PlayerHuman.transform.position;
            }
            speed = Vector3.Distance(PlayerHuman.transform.position, PreviousPos) / Time.deltaTime;
            PreviousPos = PlayerHuman.transform.position;
        }
        public void SortEnvironment(string map_name)
        {
            // if map_name is 0 we are in lobby
            if (map_name == "0")
                Destroy(Utilities.GameObjectFind("sign_modoftheyear"));
            if (map_name == "Ced's Downhill Park-1.0")
            {
                string[] strs = new string[] { "C1", "C2", "C3", "C4", "C1.5" };
                foreach (string str in strs)
                {
                    Utilities.GameObjectFind(str).tag = "Checkpoint";
                }
                // Pos -449.2, 1698.8, 488.9
                // rot 7, 86, 359
                // instantiate new checkpoint
                GameObject CP = GameObject.CreatePrimitive(PrimitiveType.Cube);
                CP.transform.position = new Vector3(-449, 1698, 488);
                CP.transform.SetPositionAndRotation(
                    new Vector3(-449, 1698, 488),
                    Quaternion.Euler(7, 86, 359)
                );
                CP.transform.localScale = new Vector3(15, 15, 1);
                CP.GetComponent<BoxCollider>().isTrigger = true;
                CP.GetComponent<MeshRenderer>().enabled = false;
                CP.tag = "Checkpoint";
            }
        }
        #region 'on' methods
        public void OnRespawn(){
            SplitTimerText.Instance.hidden = true;
			NetClient.Instance.SendData("RESPAWN");
		}
		public void OnBikeSwitch(string new_bike){
			NetClient.Instance.SendData("BIKE_SWITCH", new_bike);
		}
		public void OnBoundaryEnter(string trail_name, string boundary_guid){
			NetClient.Instance.SendData("BOUNDARY_ENTER", trail_name, boundary_guid);
		}
		public void OnBoundaryExit(string trail_name, string boundary_guid, string boundary_obj_name){
			NetClient.Instance.SendData("BOUNDARY_EXIT", trail_name, boundary_guid, boundary_obj_name);
		}
		public void OnCheckpointEnter(string trail_name, string type, int total_checkpoints, string client_time, string hash){
			NetClient.Instance.SendData("CHECKPOINT_ENTER", trail_name, type, total_checkpoints, client_time, hash);
		}
		public void OnMapEnter(string map_name){
            Utilities.Log("Map Change Detected");
            if (NetClient.Instance != null)
                NetClient.Instance.SendData("MAP_ENTER", map_name);
            if (CustomDiscordManager.instance != null)
                StartCoroutine(CustomDiscordManager.instance.ChangeMapPresence(map_name));
            else
                Debug.LogWarning("CustomDiscordManager does not exist yet..");
            // if not a bike park or a mod
            if (!Utilities.instance.isBikePark() && !Utilities.instance.isMod() && !(map_name == "0"))
            {
                StatsModification.instance.ResetStats();
                StatsModification.instance.permitted = false;
            }
            else
                StatsModification.instance.permitted = true;
            // if we're in a mod, fix the playlist
            if (Utilities.instance.isMod())
                Utilities.instance.NormaliseModSongs();
            // get rid of any environment items we hate
            try { SortEnvironment(map_name);}
            catch { }
            prevMap = map_name;
        }
		public void OnMapExit(){
			NetClient.Instance.SendData("MAP_EXIT");
		}
        #endregion
    }
}
