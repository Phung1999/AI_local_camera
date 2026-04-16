import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __iter__(self):
        return iter((self.x, self.y))
    
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Point index out of range")
    
    def __tuple__(self):
        return (self.x, self.y)


class Polygon:
    def __init__(self, points):
        if isinstance(points, list) and len(points) > 0:
            if isinstance(points[0], (int, float)):
                if len(points) >= 3:
                    pts = []
                    for i in range(0, len(points), 2):
                        if i + 1 < len(points):
                            pts.append((points[i], points[i + 1]))
                    points = pts
            elif isinstance(points[0], tuple):
                pts_flat = []
                for p in points:
                    pts_flat.append((p[0], p[1]))
                points = pts_flat
        
        self.points = points
    
    def contains(self, point):
        if isinstance(point, tuple):
            point = Point(point[0], point[1])
        return self._point_in_polygon(point.x, point.y, self.points)
    
    def _point_in_polygon(self, x, y, polygon):
        n = len(polygon)
        if n < 3:
            return False
        
        inside = False
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    @property
    def exterior(self):
        return PolygonCoords(self.points)
    
    @property
    def coords(self):
        return self.points


class PolygonCoords:
    def __init__(self, points):
        self._points = points
    
    def __iter__(self):
        return iter(self._points)


class Zone:
    def __init__(self):
        self.polygon = None

    def set_polygon(self, points):
        if len(points) < 3:
            raise ValueError("Polygon cần ít nhất 3 điểm")
        
        pts = []
        for p in points:
            if hasattr(p, 'x'):
                pts.append((p.x(), p.y()))
            elif isinstance(p, tuple):
                pts.append(p)
            else:
                raise ValueError("Invalid point format")
        
        self.polygon = Polygon(pts)

    def is_inside(self, point):
        if self.polygon is None:
            return False
        
        if isinstance(point, tuple):
            return self.polygon.contains(point)
        elif hasattr(point, 'x'):
            return self.polygon.contains((point[0], point[1]) if hasattr(point, '__getitem__') else (point.x(), point.y()))
        
        return False

    def clear(self):
        self.polygon = None

    def get_polygon(self):
        return self.polygon


if __name__ == "__main__":
    zone = Zone()
    
    rect_points = [(100, 100), (300, 100), (300, 300), (100, 300)]
    zone.set_polygon(rect_points)
    
    test_points = [
        (200, 200),
        (50, 50),
        (150, 150),
        (400, 400),
    ]
    
    for pt in test_points:
        result = zone.is_inside(pt)
        print(f"Point {pt}: {'INSIDE' if result else 'OUTSIDE'}")
