from fastapi import FastAPI , Path , HTTPException ,Query
from pydantic import BaseModel ,Field ,computed_field 
from typing import Annotated    
import json
class patient(BaseModel):
    id:Annotated [str ,Field(...,description="Enter id ")]
    name:Annotated [str,Field(...,description="Enter your name")]    
    city:Annotated [str,Field (...,description="Enter your city")]
    number : Annotated [int , Field (...,description="Enter your phone no")]
    age : Annotated [int,Field (...,gt=0 , le=120 ,description="Enter your age")]
    height :Annotated[float, Field (..., gt=0, description= "enter your height")]
    weight : Annotated[float, Field (..., gt=0, description= "enter your weight")]

    @computed_field
    @property
    def bmi(self) -> float:
        h_meters = self.height / 100
        return round(self.weight / (h_meters ** 2), 2)

app = FastAPI()

def load_data():
    with open ('patient.json' ,'r' ) as f:
        data = json.load(f)
    return data

def save_data(data):
    with open ('patient.json','w') as f:
        json.dump(data , f)
        
def for_del(data):
    with open ('patient.json','w') as f:
        json.dump(data , f ,indent=4 , sort_keys=True)
        
@app.get("/")
def welcome():
    return{"message":"welcome doct chhose the patient operation"}

@app.get("/view_all")
def view_all():
    data = load_data()
    return data

@app.get("/view_by_id/{id}")
def view(id:str = Path(...,description = 'ID of tha patient is number' , example = '001')):
    data = load_data()
    if id in data:
        return data[id]
    raise HTTPException (status_code=404 , detail="Id not found")

@app.get("/sort_by")
def sort_by(s_by:str = Query(..., description= 'Sort based on height weight and bmi') ,order:str =Query ('asc',description="Enter the on which order you wants the values to be asc or dsc")):
    val_feild = ['height' , 'weight' ,'bmi']
    if s_by not in val_feild:
        raise HTTPException(status_code=400,detail="plese enter  height or weight or bmi")
    if order not in ['asc' , 'dec']:
        raise HTTPException(status_code=400,detail="plese enter asc or dec nothing else")
    data = load_data()
    all_p = list(data.values())
    rev = (order == "dec")
    all_p.sort(key=lambda x: x.get(s_by, 0), reverse=rev)
    return all_p 

@app.get("/by_filter")
def by_filter(s_by:str = Query(..., description= 'Sort based on height weight and bmi'),search_val :float = Query(...,description="enter yout height")):
    data = load_data()
    all_patients = list(data.values())
    filtered_list = [p for p in all_patients if p.get(s_by, 0) == search_val]
    filtered_list.sort(key=lambda x: x.get(s_by, 0))
    if not filtered_list:
        raise HTTPException(status_code=404, detail=f"No patients found with {s_by} == {search_val}")
    return filtered_list

@app.post("/create")
def create(patient:patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400,detail="Id is already exists ")
    data[patient.id]= patient.model_dump(exclude=['id'])
    
    save_data(data)
    
    return{"message":"Done data entered"}

@app.delete("/delete/{id}")
def delete(id:str): 
    data = load_data()
    if id in data:
        data.pop(id)
        for_del(data)
        return (f"Delete id = {id}")
    else:
        raise HTTPException (status_code= 404, detail=f"{id}id is not found")
    
    