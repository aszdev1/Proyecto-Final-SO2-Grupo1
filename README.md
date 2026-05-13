# Proyecto-Final-SO2-Grupo1

## Ambiente de desarrollo

### Version backend python 
Python 3.13.7

Copiar .env.example -> Renombrar a .env

```powershell
cd C:\Proyecto-Final-SO2-Grupo1\backend
```

```powershell
pip install -r requirements.txt

uvicorn main:app --reload
```


## Documentacion
http://localhost:3000/docs

## Insertar evento

curl -X POST http://localhost:3000/event \
-H "Content-Type: application/json" \
-d '{"evento":"sensor","estado":"activo"}'

## Index
http://localhost


## Compilar

```powershell
build.bat
```
