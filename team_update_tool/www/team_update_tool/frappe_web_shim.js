/* ============================================================
   team_update_tool - frappe-web shim
   ------------------------------------------------------------
   Minimal stand-in for frappe-web.bundle.js so the website portal
   works on sites running WITHOUT "bench build" (i.e. when
   /assets/frappe/dist/js/frappe-web.bundle.*.js is unavailable).

   Frappe's base.html already defines the bare "frappe" object and
   a "frappe.ready" function that only queues callbacks into
   "frappe.ready_events", and injects "frappe.csrf_token" inline via
   the "csrf_token" placeholder. The real bundle is what processes
   the queue and provides frappe.call().

   This file (loaded via hooks.web_include_js on every website page):
     1) fires the callbacks queued through frappe.ready() once the
        DOM is ready, and
     2) provides frappe.call() backed by fetch() when the real one
        is missing.

   It does nothing when the real bundle has already loaded.

   NOTE: keep this file free of Jinja tag delimiters - a double
   open curly brace, or an open curly brace followed by a percent
   sign - because it is served through Frappe's Jinja renderer.
   ============================================================ */
(function () {
    "use strict";
    var w = window;

    /* Fallback for pages that use tutToast() but do not define it
       (only dashboard.html defines it; project.html uses it too).
       Runs before the bundle check so it applies in all environments;
       a page-level definition would simply override this one. */
    if (typeof w.tutToast !== "function") {
        w.tutToast = function (message, type) {
            type = type || "info";
            var container = document.querySelector(".erp-toast-container")
                || document.querySelector(".tut-toast-container");
            if (!container) {
                container = document.createElement("div");
                container.className = "erp-toast-container";
                container.style.cssText = "position:fixed;top:20px;right:20px;z-index:9999;"
                    + "display:flex;flex-direction:column;gap:10px;";
                document.body.appendChild(container);
            }
            var colors = { info: "#3b82f6", success: "#22c55e", error: "#ef4444", warning: "#f59e0b" };
            var bg = colors[type] || "#3b82f6";
            var toast = document.createElement("div");
            toast.style.cssText = "background:#fff;border-left:4px solid " + bg
                + ";border-radius:0.5rem;padding:12px 16px;box-shadow:0 4px 16px rgba(0,0,0,0.1);"
                + "font-size:0.9rem;color:#1e293b;max-width:360px;margin-bottom:8px;";
            toast.textContent = message;
            container.appendChild(toast);
            setTimeout(function () {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 4000);
        };
    }

    /* If the real bundle is present, frappe.call exists - do nothing. */
    if (!w.frappe || typeof w.frappe.call === "function") {
        return;
    }

    function runWhenReady(fn) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", fn);
        } else {
            fn();
        }
    }

    /* Match the real bundle: run callbacks immediately if the DOM is
       already ready, otherwise queue them for DOMContentLoaded. */
    if (typeof w.frappe.ready === "function") {
        var origReady = w.frappe.ready;
        w.frappe.ready = function (fn) {
            if (document.readyState === "loading") {
                origReady(fn);
            } else {
                fn();
            }
        };
    }

    /* 1) Fire queued frappe.ready() callbacks after the DOM is ready. */
    runWhenReady(function () {
        var events = (w.frappe.ready_events || []).slice(0);
        w.frappe.ready_events = [];
        for (var i = 0; i < events.length; i++) {
            try {
                events[i]();
            } catch (err) {
                console.error("frappe.ready callback error:", err);
            }
        }
    });

    /* 2) Provide frappe.call() via fetch(). */
    w.frappe.call = function (opts) {
        opts = opts || {};
        var method = opts.method || "";
        var args = opts.args || {};
        var token = w.frappe.csrf_token || w.csrf_token || "";
        var url = "/api/method/" + method;
        var pairs = [];

        for (var key in args) {
            if (Object.prototype.hasOwnProperty.call(args, key)) {
                var val = args[key];
                if (val === undefined || val === null) {
                    continue;
                }
                pairs.push(encodeURIComponent(key) + "=" + encodeURIComponent(val));
            }
        }

        var request;
        if (token) {
            /* POST like the real frappe.call, with the CSRF token that
               Frappe injects into the page for logged-in sessions. */
            request = {
                method: "POST",
                headers: {
                    "X-Frappe-CSRF-Token": token,
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
                body: pairs.join("&")
            };
        } else {
            /* No token (e.g. guest session): use GET, which works for
               whitelisted read methods without CSRF. */
            request = { method: "GET", headers: {} };
            if (pairs.length) {
                url = url + "?" + pairs.join("&");
            }
        }

        return fetch(url, request)
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (typeof opts.callback === "function") {
                    opts.callback(data);
                }
                if (typeof opts.always === "function") {
                    opts.always(data);
                }
                return data;
            })
            .catch(function (err) {
                if (typeof opts.error === "function") {
                    opts.error(err);
                }
                if (typeof opts.always === "function") {
                    opts.always(err);
                }
            });
    };
})();
