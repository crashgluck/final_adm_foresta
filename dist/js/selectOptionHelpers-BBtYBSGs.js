import{A as n}from"./apiPaths-Cf7wdpEA.js";import{u as r}from"./useSelectOptions-hpAGqTyU.js";function s(){return r(n.parcels,e=>e.codigo_parcela)}function u(){return r(n.people,e=>e.nombre_completo||e.email||`Persona ${e.id}`)}function l(e,o){return e.find(t=>String(t.value)===String(o))?.label||o||"-"}export{u as a,l as o,s as u};
//# sourceMappingURL=selectOptionHelpers-BBtYBSGs.js.map
