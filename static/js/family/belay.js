window.belay = function (t) {
    "use strict";
    function e(t, e) {
        var a = document.createElementNS("http://www.w3.org/2000/svg", t);
        return (
            Object.keys(e).forEach(function (t) {
                return a.setAttribute(t, e[t]);
            }),
            a
        );
    }
    var a = { anchor: "middle", anchorOffset: 0, animate: !0, curve: 0.66, maxArc: 50, plane: "horizontal", ropes: "yes", selectors: null, strokeWidth: 2 },
        r = Object.assign(a, t),
        n = r.animate,
        o = r.ropebagElm;
    if (o) {
        o.innerHTML = "";
        var i = o.getBoundingClientRect(),
            l = i.left,
            c = i.top;
        r.selectors.forEach(function (a) {
            if (void 0 !== a) {
                var i = document.getElementById(a);
                if (i) {
                    var h = i.getBoundingClientRect(),
                        s = h.height,
                        p = h.width;
                    if (0 !== s && 0 !== p) {
                        var d = h.left,
                            u = h.top,
                            f = document.querySelectorAll("." + a);
                        if (f.length) {
                            var g = [];
                            f.forEach(function (t) {
                                if (t) {
                                    var e = t.getBoundingClientRect(),
                                        a = e.height,
                                        n = e.width;
                                    if (0 !== a && 0 !== n) {
                                        var o = e.left,
                                            i = e.top,
                                            h = d === o ? "top" : r.anchor,
                                            f = d === o ? "vertical" : r.plane,
                                            v = "horizontal" === f ? (d > o ? "left" : "right") : u > i ? "up" : "down",
                                            w = r.strokeWidth / 2,
                                            m = d - l + ("horizontal" === f ? ("right" === v ? p : 0) : p / 2 - w),
                                            b = u - c + ("horizontal" === f ? ("top" === h ? r.anchorOffset : s / 2 - w) : "up" === v ? 0 : s),
                                            k = o - l + ("horizontal" === f ? ("right" === v ? 0 : n) : n / 2 - w),
                                            C = i - c + ("horizontal" === f ? ("top" === h ? r.anchorOffset : a / 2 - w) : "up" === v ? a : 0),
                                            z = ("horizontal" === f ? ("right" === v ? o - (d + p) : d - (o + n)) : "up" === v ? u - (i + a) : i - (u + s)) * r.curve,
                                            I = "horizontal" === f ? ("right" === v ? m + z : m - z) : m,
                                            E = "vertical" === f ? ("up" === v ? b - z : b + z) : b,
                                            y = "horizontal" === f ? ("right" === v ? k - z : k + z) : k,
                                            A = "vertical" === f ? ("up" === v ? C + z : C - z) : C;
                                        g.push({ draw: "M" + parseInt(m) + "," + parseInt(b) + " C" + parseInt(I) + "," + parseInt(E) + " " + parseInt(y) + "," + parseInt(A) + " " + parseInt(k) + "," + parseInt(C), id: t.id });
                                    }
                                }
                            });
                            var v = e("svg", { class: "svg svgCC", focusable: "false" });
                            o.appendChild(v);
                            var w = e("g", { class: "group " + r.stroke });
                            v.appendChild(w);
                            var m = window.getComputedStyle(w).backgroundColor;
                            g.forEach(function (a) {
                                var o = e("path", { class: n ? "path pathAnimate" : "path", d: a.draw, fill: "none", stroke: m, "stroke-width": r.strokeWidth });
                                w.appendChild(o),
                                    n && t.callback
                                        ? (o.setAttribute("style", "--L:" + o.getTotalLength() + ";"),
                                          o.addEventListener("animationend", function () {
                                              return t.callback(a.id), { once: !0 };
                                          }))
                                        : t.callback && t.callback(a.id);
                            });
                        }
                    }
                }
            }
        });
    }
};
//# sourceMappingURL=belay-0baa28a7.min.js.map