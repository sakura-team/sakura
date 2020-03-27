import re

GEOJSON_BBOX = '''{
    "type": "Polygon",
    "crs": {
        "type": "name",
        "properties": {
            "name": "%(srid)s"
        }
    },
    "coordinates": [[
        [%(min_longitude)s, %(min_latitude)s],
        [%(min_longitude)s, %(max_latitude)s],
        [%(max_longitude)s, %(max_latitude)s],
        [%(max_longitude)s, %(min_latitude)s],
        [%(min_longitude)s, %(min_latitude)s]
    ]]
}'''
GEOJSON_BBOX = re.sub(r"\s+", "", GEOJSON_BBOX)

class GeoBoundingBox:
    def __init__(self, min_latitude = None, max_latitude = None, min_longitude = None, max_longitude = None):
        self.min_latitude = min_latitude
        self.max_latitude = max_latitude
        self.min_longitude = min_longitude
        self.max_longitude = max_longitude
        self.srid = 'EPSG:4326'
    def as_dict(self):
        return { 'min_latitude': self.min_latitude,
                 'max_latitude': self.max_latitude,
                 'min_longitude': self.min_longitude,
                 'max_longitude': self.max_longitude }
    def as_tuple(self):
        return (self.min_latitude, self.max_latitude, self.min_longitude, self.max_longitude)
    def is_fully_defined(self):
        return None not in self.as_tuple()
    def is_blank(self):
        return all(v is None for v in self.as_tuple())
    def copy(self):
        return GeoBoundingBox(*self.as_tuple())
    def intersect(self, other):
        merged = {}
        for attr, val_self in self.as_dict().items():
            val_other = getattr(other, attr)
            if val_self is None:
                merged[attr] = val_other
            elif val_other is None:
                merged[attr] = val_self
            else:
                attr_prefix = attr[:3]
                if attr_prefix == 'min':
                    # we intersect => we keep the highest min
                    merged[attr] = val_other if (val_self < val_other) else val_self
                else:
                    # we intersect => we keep the lowest max
                    merged[attr] = val_other if (val_self > val_other) else val_self
        return GeoBoundingBox(**merged)
    def __contains__(self, val):
        if self.is_blank():
            return True
        conds = ()
        if self.min_latitude is not None:
            cond = (val.Y > self.min_latitude)
            conds += (cond,)
        if self.max_latitude is not None:
            cond = (val.Y < self.max_latitude)
            conds += (cond,)
        if self.min_longitude is not None:
            cond = (val.X > self.min_longitude)
            conds += (cond,)
        if self.max_longitude is not None:
            cond = (val.X < self.max_longitude)
            conds += (cond,)
        res = conds[0]
        for cond in conds[1:]:
            res = res & cond
        return res
    def as_geojson(self):
        # format to a geojson polygon
        return GEOJSON_BBOX % dict(
            srid = self.srid,
            **self.as_dict()
        )
