# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ActionExecuted
from swiplserver import PrologMQI, PrologThread
from rasa_sdk.events import SlotSet
import json
import csv



## Estructura para guardar el estado
chatbot_state = {
    "nombre_usuario": "",
    "framework": "",
    "version": "",
    "decisionFrame": False,
    "decisionVersion": False,
    "versionACambiar": "",
    "frameACambiar": "",
    "horasMaximas": 1,
    "trabajos": []
}
class ActionVerificarNombre(Action):
    def name(self) -> Text:
        return "action_session_start"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        print("STARTT")
        slots_to_set = {
            "s_nombre_user": chatbot_state["nombre_usuario"],
            "s_framework": chatbot_state["framework"],
            "s_version": chatbot_state["version"],
            "s_decision_framework": chatbot_state["decisionFrame"],
            "s_decision_version": chatbot_state["decisionVersion"]
        }
        dispatcher.utter_message(f"Buenass {chatbot_state['nombre_usuario']}")
        return [SlotSet(slot, value) for slot, value in slots_to_set.items()]
        

class ActionGuardarNombre(Action):
    def name(self) -> Text:
        return "action_verificar_nombre"
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        nombre_ingresado = tracker.get_slot("s_nombre_user")
        chatbot_state["nombre_usuario"] = nombre_ingresado
        guardar_estado(chatbot_state, "State.json")
        dispatcher.utter_message(f"Gracias por tu nombre, {nombre_ingresado}\nComo estás?")
        return []

class ActionSaludoConNombre(Action):
    def name(self):
        return "action_saludo_con_nombre"
    def run(self, dispatcher, tracker, domain):
        print("Saludooo")
        nombre_usuario = chatbot_state["nombre_usuario"]
        if nombre_usuario:
            dispatcher.utter_message(f"Hola {nombre_usuario}, un gusto hablar devuelta con vos, como estás?")
        else:
            dispatcher.utter_message("Holaa, soy Ivico, cómo te llamas?")

        slots_to_set = {
            "s_nombre_user": chatbot_state["nombre_usuario"],
            "s_framework": chatbot_state["framework"],
            "s_version": chatbot_state["version"],
            "s_decision_framework": chatbot_state["decisionFrame"],
            "s_decision_version": chatbot_state["decisionVersion"],
        }

        return [SlotSet(slot, value) for slot, value in slots_to_set.items()]

class ActionUtterF(Action):
    def name(self):
        return "action_utter_framework"
    def run(self, dispatcher, tracker, domain):
        nombre_usuario = chatbot_state["nombre_usuario"]
        frame = chatbot_state["framework"]
        print("action utter frame")
        if nombre_usuario!="" and frame!="":
            dispatcher.utter_message(f"Todavía seguis usando {frame}, no?")
        elif nombre_usuario!="":
            dispatcher.utter_message("Aun no me has contado que framework usas para trabajar, contame jaja")
        return[]

class ActionGuardarFrame(Action):
    def name(self):
        return "action_guardar_frame"

    def run(self, dispatcher, tracker, domain):
        frame = tracker.get_slot("s_framework")
        chatbot_state["framework"] = frame
        print("action guardar frame")
        guardar_estado(chatbot_state, "State.json")
        dispatcher.utter_message("Y qué versión es la que usas?")
        return[]
    
class ActionVersion(Action):
    def name(self):
        return "action_version"
    def run(self, dispatcher, tracker, domain):
        v = chatbot_state["version"]
        print("action version")
        if v=="":
            dispatcher.utter_message("Y qué versión es la que usas?")
        return[]
    
    
class ActionPreguntarVersion(Action):
    def name(self):
        return "action_cambio_de_version"
    def run(self, dispatcher, tracker, domain):
        v = chatbot_state["versionACambiar"]
        chatbot_state["version"] = v
        chatbot_state["decisionVersion"] = False
        print("action update version")
        guardar_estado(chatbot_state, "State.json")
        dispatcher.utter_message(f"Entonces te cambiaste a la versión {v} ? te dije que era mejor jaja")
        return[SlotSet("s_decision_version", False)]
    

class ActioncambioDeFrame(Action):
    def name(self):
        return "action_cambio_de_framework"
    def run(self, dispatcher, tracker, domain):
        f = chatbot_state["frameACambiar"]
        chatbot_state["framework"] = f
        chatbot_state["decisionFrame"] = False
        print("action update framework")
        guardar_estado(chatbot_state, "State.json")
        dispatcher.utter_message(f"Entonces te cambiaste a {f} ? Está perfecto, es para mejor jaja\nQué version estás usando?")
        return[SlotSet("s_decision_framework", False)]
    
class ActionGuardarversion(Action):
    def name(self) -> Text:
        return "action_guardar_version"  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            v = tracker.get_slot("s_version")
            print("guardarVersionnn: ", v)
            chatbot_state["version"] = v
            guardar_estado(chatbot_state, "State.json")
            dispatcher.utter_message("joyaa")
            return[]

def guardar_estado(chatbot_state, nombre_archivo):
    with open(nombre_archivo, 'w') as archivo:
        json.dump(chatbot_state, archivo)

def cargar_estado(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return {}

######      CARGA DEL ESTADO DEL CHATBOT      ######
chatbot_state=cargar_estado("State.json")
print("nombre",chatbot_state["nombre_usuario"])
#
# completar
#
#


class ActionConenctProlog(Action):

    def name(self) -> Text:
        return "action_pedir_versiones_rasa"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            with PrologMQI(port=8000) as mqi:
                with mqi.create_thread() as prolog_thread:
                    prolog_thread.query_async(r"consult('C:\\Users\\User\\rasa\\Rasa_Proyects\\data\\universe.pl')", find_all=False)
                    prolog_thread.query_async(f"findall(Version, framework(rasa, Version), Versiones).", find_all=False)
                    result = prolog_thread.query_async_result()[0]['Versiones']
                    dispatcher.utter_message(f"Las últimas versiones que conozco son las: \n")
                    for v in result:
                        dispatcher.utter_message(text=f"- {v}")
            return[]


class ActionGuardarHS(Action):
    def name(self) -> Text:
        return "action_guardar_hs_max"  
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        h = int(tracker.get_slot("s_cant_horas"))
        print("guardarHss: ", h)
        chatbot_state["horasMaximas"] = h
        guardar_estado(chatbot_state, "State.json")
        suma=0
        for trabajo in chatbot_state["trabajos"]:
            suma= suma+trabajo[1]
        if(suma>h):
            dispatcher.utter_message("Che igual fijate que tenés más horas acumuladas con tus trabajos que la cantidad de horas disponibles..")
            dispatcher.utter_message("Si terminaste algun trabajo decime el nombre y vemos que onda")
        else:
            dispatcher.utter_message("Si tenés algun trabajo que estás haciendo o algo contame")            
        return[]
    


class ActionIsOrUpTrabajo(Action):
    def name(self) -> Text:
        return "action_hs_trabajo"  
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nombre = tracker.get_slot("s_nombre_trabajo")
        horas = int(tracker.get_slot("s_cant_horas"))
        print("guardarTrabajo: ", nombre, " - ", horas)
        if(tracker.latest_message['intent'].get('name') == "nuevo_trabajo"):
            suma=0
            chatbot_state["trabajos"].append((nombre,horas))
            dispatcher.utter_message("Listoo, lo tengo agendado")  
            for trabajo in chatbot_state["trabajos"]:
                suma= suma+trabajo[1]
            if(suma>chatbot_state["horasMaximas"]):
                dispatcher.utter_message("Tené en cuenta que superas la cantidad de horas disponbles que tenés a la semana") 
        else:
            for i in range(len(chatbot_state["trabajos"])):
                if(chatbot_state["trabajos"][i][0] == nombre):
                    chatbot_state["trabajos"][i] = [nombre,horas]
                    dispatcher.utter_message(f"Listoo, ya actualizo el tiempo de trabajo de {nombre}") 
                    guardar_estado(chatbot_state, "State.json")    
                    return []        
        guardar_estado(chatbot_state, "State.json")          
        return[]


class ActionFinTrabajo(Action):
    def name(self) -> Text:
        return "action_fin_trabajo"  
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        nombre = tracker.get_slot("s_nombre_trabajo")
        print("FinTrabajo: ", nombre)
        for i in range(len(chatbot_state["trabajos"])):
            if(chatbot_state["trabajos"][i][0] == nombre):
                del chatbot_state["trabajos"][i]
                dispatcher.utter_message(f"Listo, bien al terminar con {nombre}") 
                guardar_estado(chatbot_state, "State.json")    
                return []
            else:
                print("elsee :(", chatbot_state["trabajos"][i], " | " , nombre)
        dispatcher.utter_message(f"Mmmm, seguro que es {nombre}?\nO no me habías contado de ese o quizas me lo contaste con otro nombre")         
        return[]

class ActionDarrHS(Action):
    def name(self) -> Text:
        return "action_dar_horas_trabajo"  
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        suma=0
        print("horas acumulado")
        for trabajo in chatbot_state["trabajos"]:
            suma= suma+trabajo[1]
        dispatcher.utter_message(f"Por lo que me has contado tenes {suma} horas semanales de trabajo")            
        return[]


class ActionDarrTr(Action):
    def name(self) -> Text:
        return "action_dar_trabajos"  
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("Trabajos...")
        if[len(chatbot_state["trabajos"])]==0:
            dispatcher.utter_message("No tengo registro de ningún trabajo hasta el momento, si queres contame sobre alguno nuevo")    
        for trabajo in chatbot_state["trabajos"]:
            dispatcher.utter_message(f"Nombre: {trabajo[0]} | Horas semanales dedicadas: {trabajo[1]}")            
        return[]


class ActionConenctProlog2(Action):
    def name(self) -> Text:
        return "action_verificar_ultima_version"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            print("verificar ultima version")
            frame = chatbot_state["framework"] 
            version = chatbot_state["version"]
            print("frame", frame ,"  -  version: ", version)
            booleano = False
            with PrologMQI(port=8000) as mqi:
                with mqi.create_thread() as prolog_thread:
                    prolog_thread.query_async(r"consult('C:\\Users\\User\\rasa\\Rasa_Proyects\\data\\universe.pl')", find_all=False)
                    prolog_thread.query_async(f"findall(Version, ultima_version({frame}, Version), Resultado).", find_all=False)
                    result = prolog_thread.query_async_result()[0]['Resultado']
                    print(result[0])
                    if(result[0] == version):  #es la ultima version
                        booleano = True
                        dispatcher.utter_message(f"See papaa, tenes la ultima versión")
                    else:
                        dispatcher.utter_message(f"negativo chee.. no tenes la última version :(\nTengo información de la ultima version si querés")
            print("fin verificar ultima version: ", booleano)
            return[]
    

class ActionConenctProlog3(Action):
    def name(self) -> Text:
        return "action_dar_detalles_ult_version"    #es el que da las mejoras de las versiones.
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            frame = chatbot_state["framework"] #Está bien usar el slot en este caso? NO, CAMBIAR POR LO QUE DIGA EL ESTADO DEL CHATBOT.
            with PrologMQI(port=8000) as mqi:
                with mqi.create_thread() as prolog_thread:
                    prolog_thread.query_async(r"consult('C:\\Users\\User\\rasa\\Rasa_Proyects\\data\\universe.pl')", find_all=False)
                    prolog_thread.query_async(f"findall(Version, ultima_version({frame}, Version), Resultado).", find_all=False)
                    result1 = prolog_thread.query_async_result()[0]['Resultado']
                    print(f"consulta: {frame}, '{result1[0]}'") 
                    chatbot_state["versionACambiar"]=result1[0]
                    guardar_estado(chatbot_state, "State.json")
                    prolog_thread.query_async(r"consult('C:\\Users\\User\\rasa\\Rasa_Proyects\\data\\universe.pl')", find_all=False)
                    prolog_thread.query_async(f"findall(Mejoras, mejora({frame}, '{result1[0]}' , Mejoras), Resultado2).", find_all=False)
                    result = prolog_thread.query_async_result()[0]['Resultado2']
                    dispatcher.utter_message(f"Las mejoras de la última version ({result1[0]}) son: \n")
                    for v in result:
                        dispatcher.utter_message(text=f"- {v}")
            return[] 
    
class ActionGuardarDecision(Action):
    def name(self) -> Text:
        return "action_anotar_decision_version"  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            print("decision version")
            decision = tracker.get_slot("s_decision_version")
            chatbot_state["decisionVersion"] = decision
            guardar_estado(chatbot_state, "State.json")
            if decision:
                dispatcher.utter_message("Listoo, suerte con eso")
            else:
                dispatcher.utter_message("Bueno pa, no hay drama con eso")
            return []


class ActionConenctProlog6(Action):
    def name(self) -> Text:
        return "action_dar_opciones_frame"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            frame = chatbot_state["framework"] 
            with PrologMQI(port=8000) as mqi:
                with mqi.create_thread() as prolog_thread:
                    prolog_thread.query_async(r"consult('C:\\Users\\User\\rasa\\Rasa_Proyects\\data\\universe.pl')", find_all=False)
                    prolog_thread.query_async(f"findall(Version, compatible({frame}, Version), Resultado).", find_all=False)
                    result = prolog_thread.query_async_result()[0]['Resultado']
                    dispatcher.utter_message(f"Los framework a los que podrías emigrar que sean compatibles son: \n")
                    for v in result:
                        dispatcher.utter_message(text=f"- {v}")
            return []
    

class ActionConenctProlog6(Action):
    def name(self) -> Text:
        return "action_dar_detalles_de_x"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            frame = tracker.get_slot("s_framework")
            print("detalle de ",frame)
            with PrologMQI(port=8000) as mqi:
                with mqi.create_thread() as prolog_thread:
                    prolog_thread.query_async(r"consult('C:\\Users\\User\\rasa\\Rasa_Proyects\\data\\universe.pl')", find_all=False)
                    prolog_thread.query_async(f"findall(Detalle, detalle({frame}, Detalle), Resultado).", find_all=False)
                    result = prolog_thread.query_async_result()[0]['Resultado']
                    dispatcher.utter_message(f"Los detelles de {frame} son: \n")
                    for v in result:
                        dispatcher.utter_message(text=f"- {v}")
            return []
    
class ActionGuardarDecisionFrame(Action):
    def name(self) -> Text:
        return "action_guardar_decision_frame"  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            print("guardar decision frame")
            frame = tracker.get_slot("s_framework")
            chatbot_state["decisionFrame"] = True
            chatbot_state["frameACambiar"] = frame
            guardar_estado(chatbot_state, "State.json")
            dispatcher.utter_message("Seguro lo logras y te resulta mejor!")
            return [SlotSet("s_decision_framework", True)]


class ActionGuardarDecisionFrame(Action):

    def name(self) -> Text:
        return "action_despedida"  

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            dispatcher.utter_message("Hasta luego ",chatbot_state["nombre_usuario"])
            guardar_estado(chatbot_state, "State.json")
            return []


