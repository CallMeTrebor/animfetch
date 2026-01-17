#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cmath>
#include <random>
#include <string>
#include <vector>

#include "planet.hpp"

namespace py = pybind11;

static py::tuple updateStars(py::list frame, int width, int height,
                             py::list star_data, double delta_time = 0.0) {
  // Compute max stars (2% of pixels)
  const int64_t maxStars = static_cast<int64_t>(std::floor(
      static_cast<double>(width) * static_cast<double>(height) * 0.02));

  // RNG setup
  static thread_local std::mt19937_64 rng{std::random_device{}()};
  std::uniform_real_distribution<double> uRand(0.0, 1.0);
  std::uniform_int_distribution<int> randX(0, std::max(0, width - 1));
  std::uniform_int_distribution<int> randY(0, std::max(0, height - 1));

  // Add new star with the same probability logic as Python
  const double baseStarGenRate = 0.07;
  const double starGenChance =
      std::min(baseStarGenRate * 1.0 / (delta_time + baseStarGenRate), 1.0);
      
  if (static_cast<py::ssize_t>(star_data.size()) < maxStars &&
      uRand(rng) > starGenChance) {
    int x = width > 0 ? randX(rng) : 0;
    int y = height > 0 ? randY(rng) : 0;
    // brightness randomly chosen from [".", "*", "+"]
    double r = uRand(rng);
    const char *b = ".";
    if (r < 1.0 / 3.0)
      b = ".";
    else if (r < 2.0 / 3.0)
      b = "*";
    else
      b = "+";
    star_data.append(py::make_tuple(x, y, py::str(b)));
  }

  // Transition probabilities scaled by delta_time
  const double brightenRate = 0.25;
  const double dimRate = 0.5;
  const double brightenChance = std::min(brightenRate * delta_time, 1.0);
  const double dimChance = std::min(dimRate * delta_time, 1.0);

  py::list newStarData;

  for (py::handle item : star_data) {
    auto tup = py::cast<py::tuple>(item);
    int x = py::cast<int>(tup[0]);
    int y = py::cast<int>(tup[1]);
    std::string brightness = py::cast<std::string>(tup[2]);

    double rv = uRand(rng);
    std::string newBrightness = brightness;
    if (rv < brightenChance) {
      if (brightness == ".")
        newBrightness = "*";
      else if (brightness == "*")
        newBrightness = "+";
      else
        newBrightness = "+";
    } else if (rv < brightenChance + dimChance) {
      if (brightness == "+")
        newBrightness = "*";
      else if (brightness == "*")
        newBrightness = ".";
      else
        newBrightness = "!"; // mark for removal
    }

    // Keep if not marked for removal
    if (newBrightness != "!") {
      newStarData.append(py::make_tuple(x, y, py::str(newBrightness)));
      if (0 <= x && x < width && 0 <= y && y < height) {
        // frame[y][x] = updated_brightness
        py::list row = py::cast<py::list>(frame[y]);
        row.attr("__setitem__")(x, py::str(newBrightness));
      }
    } else {
      if (0 <= x && x < width && 0 <= y && y < height) {
        py::list row = py::cast<py::list>(frame[y]);
        row.attr("__setitem__")(x, py::str(" "));
      }
    }
  }

  return py::make_tuple(frame, newStarData);
}

// Helper function to convert Python list of planet tuples to vector of Planet objects
static std::vector<Planet> planetsFromPython(py::list planet_list) {
  std::vector<Planet> planets;
  planets.reserve(planet_list.size());
  
  for (py::handle item : planet_list) {
    if (py::isinstance<Planet>(item)) {
      // Already a Planet object
      planets.push_back(py::cast<Planet>(item));
    } else if (py::isinstance<py::tuple>(item)) {
      // Convert from tuple (radius, theta) or (radius, theta, name, color)
      auto tup = py::cast<py::tuple>(item);
      double radius = py::cast<double>(tup[0]);
      double theta = py::cast<double>(tup[1]);
      
      if (tup.size() >= 4) {
        std::string name = py::cast<std::string>(tup[2]);
        RGB color = py::cast<RGB>(tup[3]);
        planets.emplace_back(radius, theta, name, color);
      } else if (tup.size() == 3) {
        std::string name = py::cast<std::string>(tup[2]);
        planets.emplace_back(radius, theta, name);
      } else {
        planets.emplace_back(radius, theta);
      }
    }
  }
  
  return planets;
}

// Helper function to convert vector of Planet objects to Python list
static py::list planetsToPython(const std::vector<Planet>& planets) {
  py::list result;
  for (const auto& planet : planets) {
    result.append(planet);
  }
  return result;
}

static py::tuple updatePlanets(py::list frame, int width, int height,
                               py::list planet_data, double delta_time = 0.0) {

  // Convert Python list to vector of Planet objects
  std::vector<Planet> planets = planetsFromPython(planet_data);
  
  // Update each planet
  for (auto& planet : planets) {
    planet.update(delta_time);
    
    // Get planet position in frame coordinates
    int centerX = width / 2;
    int centerY = height / 2;
    
    int x = centerX + static_cast<int>(std::round(planet.getX()));
    int y = centerY + static_cast<int>(std::round(planet.getY()));
    
    // Draw planet if within bounds
    if (x >= 0 && x < width && y >= 0 && y < height) {
      py::list row = py::cast<py::list>(frame[y]);
      row.attr("__setitem__")(x, py::str("O"));
    }
  }
  
  // Convert back to Python list
  py::list new_planet_data = planetsToPython(planets);

  return py::make_tuple(frame, new_planet_data);
}

PYBIND11_MODULE(planets_cpp, m) {
  m.doc() = "C++ acceleration for animfetch.providers.planets";
  
  // Expose RGB struct to Python
  py::class_<RGB>(m, "RGB")
    .def(py::init<>(), "Construct RGB with default white color (255, 255, 255)")
    .def(py::init<int, int, int>(), py::arg("r"), py::arg("g"), py::arg("b"),
         "Construct RGB with red, green, blue values (0-255)")
    .def_readwrite("r", &RGB::r, "Red component (0-255)")
    .def_readwrite("g", &RGB::g, "Green component (0-255)")
    .def_readwrite("b", &RGB::b, "Blue component (0-255)")
    .def("__repr__", [](const RGB &c) {
      return "RGB(" + std::to_string(c.r) + ", " + 
             std::to_string(c.g) + ", " + std::to_string(c.b) + ")";
    });
  
  // Expose Planet class to Python
  py::class_<Planet>(m, "Planet")
    .def(py::init<double, double>(), py::arg("radius"), py::arg("theta"),
         "Construct a Planet with radius and theta (angle in radians)")
    .def(py::init<double, double, std::string, RGB>(), 
         py::arg("radius"), py::arg("theta"), py::arg("name"), py::arg("color"),
         "Construct a Planet with radius, theta, name, and color")
    .def("get_radius", &Planet::getRadius, "Get the orbital radius")
    .def("get_theta", &Planet::getTheta, "Get the current angle in radians")
    .def("get_x", &Planet::getX, "Get the X coordinate (Cartesian)")
    .def("get_y", &Planet::getY, "Get the Y coordinate (Cartesian)")
    .def("get_name", &Planet::getName, "Get the planet name")
    .def("get_color", &Planet::getColor, "Get the planet color (RGB)")
    .def("update", &Planet::update, py::arg("delta_time"),
         "Update planet position based on delta_time")
    .def("__repr__", [](const Planet &p) {
      auto color = p.getColor();
      return "<Planet '" + p.getName() + "' radius=" + std::to_string(p.getRadius()) +
             " theta=" + std::to_string(p.getTheta()) + 
             " color=RGB(" + std::to_string(color.r) + ", " + 
             std::to_string(color.g) + ", " + std::to_string(color.b) + ")>";
    });
  
  m.def("update_stars", &updateStars, py::arg("frame"), py::arg("width"),
        py::arg("height"), py::arg("star_data"), py::arg("delta_time") = 0.0,
        R"pbdoc(
Update stars for the Planets animation.
Args:
  frame (list[list[str]]): The 2D character buffer. Modified in-place.
  width (int): frame width
  height (int): frame height
  star_data (list[tuple[int,int,str]]): Existing stars
  delta_time (float): Seconds since last frame
Returns:
  tuple[list[list[str]], list[tuple[int,int,str]]]: (frame, new_star_data)
)pbdoc");

  m.def("update_planets", &updatePlanets, py::arg("frame"), py::arg("width"),
        py::arg("height"), py::arg("planet_data"), py::arg("delta_time") = 0.0,
        R"pbdoc(
Update planets for the Planets animation.
Args:
  frame (list[list[str]]): The 2D character buffer. Modified in-place.
  width (int): frame width
  height (int): frame height
  planet_data (list): List of Planet objects or tuples (radius, theta)
  delta_time (float): Seconds since last frame
Returns:
  tuple[list[list[str]], list[Planet]]: (frame, updated_planet_list)
)pbdoc");
}
