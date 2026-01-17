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
};

class Planet {
    using planetPosition_t = double;
    using planetMoveSpeed_t = double;
    using planetType_t = float;
    planetPosition_t m_radius = planetPosition_t(10), m_theta = planetPosition_t(0);
    planetMoveSpeed_t m_speedFactor = 1 / m_radius;
    std::string m_name;
    RGB m_color;
    
public:
    Planet(planetPosition_t radius, planetPosition_t theta, std::string name = "", RGB color = RGB())
        : m_radius(radius), m_theta(theta), m_name(name), m_color(color) {}

    planetPosition_t getRadius() const { return m_radius; }
    planetPosition_t getTheta() const { return m_theta; }
    planetPosition_t getX() const { return m_radius * cos(m_theta); }
    planetPosition_t getY() const { return m_radius * sin(m_theta); }
    std::string getName() const { return m_name; }
    RGB getColor() const { return m_color; }
    void update(planetType_t deltaTime) { m_theta += deltaTime * m_speedFactor; }
};

#endif // ANIMFETCH_PLANET_HPP