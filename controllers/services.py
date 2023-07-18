from fastapi import APIRouter, Depends, status, HTTPException, Response
from dependencies import get_db
from sqlalchemy.orm import Session
from models.service import Service
from schemas import service
from crontab import CronTab
import ansible_runner

app = APIRouter(
    prefix="/services",
    tags=["services"],
    responses={404: {"description": "Not found"}}
)

# Get list of Services
@app.get("", status_code=status.HTTP_200_OK)
async def get_services(db: Session = Depends(get_db)):
  services = db.query(Service).all()
  return {"data": services}

@app.get("/{id}", status_code=status.HTTP_200_OK)
async def get_single_service(id: int, db: Session = Depends(get_db)):
  target = db.query(Service).filter(Service.id == id).first()

  if not target:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Target not found')
  
  return {"data": target}

# Add Service
@app.post("", status_code=status.HTTP_201_CREATED)
def add_service(req: service.ServiceCreate, db: Session = Depends(get_db)):
  new_svc = Service(**req.dict())
  db.add(new_svc)
  db.commit()
  db.refresh(new_svc)
  return {"status": "Service added", "data": new_svc}

# Update Service
@app.put("/{id}", status_code=status.HTTP_200_OK)
def update_status(id: int, req: service.ServiceUpdate, db: Session = Depends(get_db)):
  update_req = Service(**req.dict(exclude_unset=True))
  target_query = db.query(Service).filter(Service.id == id)
  target = target_query.first()

  if not target:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Target not found')

  parsing_vars = {
    "dest_ip": target.name
  }

  if update_req.weekday_bandwidth != None and target.weekday_bandwidth != update_req.weekday_bandwidth:
    parsing_vars["bandwidth"] = update_req.weekday_bandwidth
    runner = ansible_runner.run(private_data_dir='ansible', playbook='bandwidth_limit.yml', extravars=parsing_vars)
    if runner.status == 'failed':
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal Error')
    
    target.weekday_bandwidth = update_req.weekday_bandwidth

  if update_req.weekend_bandwidth != None and target.weekend_bandwidth != update_req.weekend_bandwidth:
    parsing_vars["bandwidth"] = update_req.weekend_bandwidth

    target.weekend_bandwidth = update_req.weekend_bandwidth


  db.merge(target)
  db.commit()
  db.refresh(target)
  return {"status": "Service updated", "data": target}

# Delete Service
@app.delete("/{id}")
def delete_service(id: int, db: Session = Depends(get_db)):
  target_query = db.query(Service).filter(Service.id == id)
  target = target_query.first()

  if not target:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Target not found')
  
  if target.is_active:
    parsing_vars = {
      "dest_ip": target.name,
      "bandwidth": target.weekday_bandwidth,
      "undo": "no"
    }
    runner = ansible_runner.run(private_data_dir='ansible', playbook='static_route.yml', extravars=parsing_vars)
  
  target_query.delete(synchronize_session=False)
  db.commit()
  return Response(status_code=status.HTTP_200_OK)