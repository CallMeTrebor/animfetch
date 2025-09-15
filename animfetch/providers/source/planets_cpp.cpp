#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cmath>
#include <random>
#include <string>

namespace py = pybind11;

// C++ implementation of update_stars mirroring the Python logic in planets.py
// Signature: (frame, width, height, star_data, delta_time) -> (frame,
// new_star_data)
// - frame: list[list[str]] (mutated in place)
// - star_data: list[tuple[int,int,str]]
// - returns: (same frame object, new star_data list)

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

  py::tuple result(2);
  result[0] = frame;       // same object, mutated
  result[1] = newStarData; // filtered list
  return result;
}

static py::tuple updatePlanets(py::list frame, int width, int height,
                               py::list planet_data, double delta_time = 0.0) {
  py::tuple result(2);
  result[0] = frame;
  result[1] = planet_data;
  return result;
}

PYBIND11_MODULE(planets_cpp, m) {
  m.doc() = "C++ acceleration for animfetch.providers.planets";
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
Update planets for the Planets animation (placeholder).
Args:
  frame (list[list[str]]): The 2D character buffer. Modified in-place.
  width (int): frame width
  height (int): frame height
  planet_data (list): Existing planet data
  delta_time (float): Seconds since last frame
Returns:
  tuple[list[list[str]], list]: (frame, new_planet_data)
)pbdoc");
}
