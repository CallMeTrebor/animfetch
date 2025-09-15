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
  const int64_t max_stars = static_cast<int64_t>(std::floor(
      static_cast<double>(width) * static_cast<double>(height) * 0.02));

  // RNG setup
  static thread_local std::mt19937_64 rng{std::random_device{}()};
  std::uniform_real_distribution<double> urand(0.0, 1.0);
  std::uniform_int_distribution<int> rand_x(0, std::max(0, width - 1));
  std::uniform_int_distribution<int> rand_y(0, std::max(0, height - 1));

  // Add new star with the same probability logic as Python
  const double base_star_gen_rate = 0.07;
  const double star_gen_chance = std::min(
      base_star_gen_rate * 1.0 / (delta_time + base_star_gen_rate), 1.0);
  if (static_cast<py::ssize_t>(star_data.size()) < max_stars &&
      urand(rng) > star_gen_chance) {
    int x = width > 0 ? rand_x(rng) : 0;
    int y = height > 0 ? rand_y(rng) : 0;
    // brightness randomly chosen from [".", "*", "+"]
    double r = urand(rng);
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
  const double brighten_rate = 0.25;
  const double dim_rate = 0.5;
  const double brighten_chance = std::min(brighten_rate * delta_time, 1.0);
  const double dim_chance = std::min(dim_rate * delta_time, 1.0);

  py::list new_star_data;

  for (py::handle item : star_data) {
    auto tup = py::cast<py::tuple>(item);
    int x = py::cast<int>(tup[0]);
    int y = py::cast<int>(tup[1]);
    std::string brightness = py::cast<std::string>(tup[2]);

    double rv = urand(rng);
    std::string new_brightness = brightness;
    if (rv < brighten_chance) {
      if (brightness == ".")
        new_brightness = "*";
      else if (brightness == "*")
        new_brightness = "+";
      else
        new_brightness = "+";
    } else if (rv < brighten_chance + dim_chance) {
      if (brightness == "+")
        new_brightness = "*";
      else if (brightness == "*")
        new_brightness = ".";
      else
        new_brightness = "!"; // mark for removal
    }

    // Keep if not marked for removal
    if (new_brightness != "!") {
      new_star_data.append(py::make_tuple(x, y, py::str(new_brightness)));
      if (0 <= x && x < width && 0 <= y && y < height) {
        // frame[y][x] = updated_brightness
        py::list row = py::cast<py::list>(frame[y]);
        row.attr("__setitem__")(x, py::str(new_brightness));
      }
    } else {
      if (0 <= x && x < width && 0 <= y && y < height) {
        py::list row = py::cast<py::list>(frame[y]);
        row.attr("__setitem__")(x, py::str(" "));
      }
    }
  }

  py::tuple result(2);
  result[0] = frame;         // same object, mutated
  result[1] = new_star_data; // filtered list
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
}
