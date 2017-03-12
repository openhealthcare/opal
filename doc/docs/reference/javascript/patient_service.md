## The Patient service

The `Patient` service in `opal.services` is the client side representation of a patient model.


### Constructor

The Patient service is instantiated with the Patient data that comes back from the Patient JSON API.
It will cast any `Episode` data to [Episode](episode_service.md) objects, and any `PatientSubrecord`
data to [Item](item_service.md) objects

```javascript
    var patient = new Patient(json_data)
```
