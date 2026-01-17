#ifndef ANIMFETCH_PLANET_HPP
#define ANIMFETCH_PLANET_HPP

#include <cmath>
#include <string>

struct RGB {
    int r;
    int g;
    int b;
    
    RGB() : r(255), g(255), b(255) {}
    RGB(int red, int green, int blue) : r(red), g(green), b(blue) {}
    
    // Return a darker version of this color
    RGB darkened(double factor = 0.4) const {
        return RGB(
            static_cast<int>(r * factor),
            static_cast<int>(g * factor),
            static_cast<int>(b * factor)
        );
    }
};

class Planet {
    using planetPosition_t = double;
    using planetMoveSpeed_t = double;
    using planetType_t = float;
    planetPosition_t m_radius = planetPosition_t(10), m_theta = planetPosition_t(0);
    planetMoveSpeed_t m_speedFactor;
    std::string m_name;
    RGB m_color;
    bool m_showPath = true;
    bool m_static = false;
    
public:
    Planet(planetPosition_t radius, planetPosition_t theta, std::string name = "", RGB color = RGB(), bool showPath = true, bool isStatic = false)
        : m_radius(radius), m_theta(theta), m_speedFactor(1.0 / radius), m_name(name), m_color(color), m_showPath(showPath), m_static(isStatic) {}

    planetPosition_t getRadius() const { return m_radius; }
    planetPosition_t getTheta() const { return m_theta; }
    planetPosition_t getX() const { return m_radius * cos(m_theta); }
    planetPosition_t getY() const { return m_radius * sin(m_theta); }
    std::string getName() const { return m_name; }
    RGB getColor() const { return m_color; }
    RGB getPathColor() const { return m_color.darkened(0.4); }
    bool getShowPath() const { return m_showPath; }
    bool getStatic() const { return m_static; }
    void update(planetType_t deltaTime) { 
        if (!m_static) {
            m_theta += deltaTime * m_speedFactor; 
        }
    }
};

#endif // ANIMFETCH_PLANET_HPP