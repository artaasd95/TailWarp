#include "wrappers/risk_metrics.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(_native, m) {
    m.doc() = "TailWarp host risk_metrics bindings (no CUDA required at import)";

    m.def(
        "compute_cvar",
        [](const std::vector<float>& returns, float alpha) {
            return tailwarp::compute_cvar(returns, alpha);
        },
        py::arg("returns"),
        py::arg("alpha") = 0.95f);

    m.def(
        "compute_var",
        [](const std::vector<float>& returns, float alpha) {
            return tailwarp::compute_var(returns, alpha);
        },
        py::arg("returns"),
        py::arg("alpha") = 0.95f);

    m.def(
        "compute_warning_state",
        [](float solvency_distance,
           float max_drawdown,
           float gross_exposure,
           float cvar_95) {
            tailwarp::WarningStateParams p{
                .solvency_distance = solvency_distance,
                .max_drawdown = max_drawdown,
                .gross_exposure = gross_exposure,
                .cvar_95 = cvar_95,
            };
            auto r = tailwarp::compute_warning_state(p);
            py::dict out;
            out["state"] = static_cast<int>(r.state);
            out["reason"] = r.reason;
            out["triggered_metrics"] = r.triggered_metrics;
            return out;
        },
        py::arg("solvency_distance"),
        py::arg("max_drawdown"),
        py::arg("gross_exposure"),
        py::arg("cvar_95"));
}
