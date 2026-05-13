db = db.getSiblingDB('eventosdb');

const collections = db.getCollectionNames();

if (!collections.includes('eventos')) {

    db.createCollection('eventos');

    db.eventos.insertOne({
        sistema: "init",
        mensaje: "Colección creada automáticamente",
        fecha: new Date()
    });

    print("Colección creada");

} else {

    print("La colección ya existe");

}