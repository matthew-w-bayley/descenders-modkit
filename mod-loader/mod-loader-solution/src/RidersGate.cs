using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace ModLoaderSolution
{
	[RequireComponent(typeof(Animator))]
	[RequireComponent(typeof(AudioSource))]
	public class RidersGate : MonoBehaviour {
		public AudioClip beforeOpen;
		public AudioClip onOpen;
		public bool gateEnabled = true;
		public void TriggerGate(float randomTime){
			if (gateEnabled)
				gateTriggerCoroutine = StartCoroutine(TriggerGateCoro(randomTime));
		}
		public void Update()
        {
            if (Input.GetKeyDown(KeyCode.G))
			{
				ToggleGate();
				UserInterface.Instance.SpecialNotif("Gates toggled: " + gateEnabled.ToString());
			}
        }
		Coroutine gateTriggerCoroutine = null;
		public void ToggleGate()
        {
			if (gateTriggerCoroutine != null)
				StopCoroutine(gateTriggerCoroutine);
			GetComponent<AudioSource>().Stop();
			GetComponent<Animator>().StopPlayback();
			if (gateEnabled)
				GetComponent<Animator>().Play("Open");
			else
				GetComponent<Animator>().Play("Close");
			gateEnabled = !gateEnabled;
        }
		IEnumerator TriggerGateCoro(float randomTime)
        {
			GetComponent<AudioSource>().PlayOneShot(beforeOpen);
			yield return new WaitForSeconds(beforeOpen.length);
			yield return new WaitForSeconds(randomTime);
			GetComponent<AudioSource>().PlayOneShot(onOpen);
			yield return new WaitForSeconds(0.365f);
			GetComponent<Animator>().Play("Open");
			yield return new WaitForSeconds(5f);
			GetComponent<Animator>().Play("Close");
		}
	}
}