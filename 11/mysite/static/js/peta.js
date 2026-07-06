/**
 * peta.js — Map logic for Peta Provinsi Indonesia
 *
 * Handles:
 *  - Leaflet map initialization with OSM tile layer
 *  - Single combined GeoJSON load for all 34 provinces
 *  - Color palette assignment per province (index-based)
 *  - Province highlight (single-highlight invariant)
 *  - Choropleth visualization (5 equal-interval classes)
 *  - Legend (default + choropleth modes)
 *  - Select2 province selector with "Cari" button
 *  - Data table sorting, filtering, and row-click interaction
 *  - Error handling with toast notifications
 *
 * Expects global variables from Django template:
 *  - window.STAT_DATA: [{prov_name, latitude, longitude, jumlah}, ...]
 *  - window.PROVINCE_LIST: [{id, name, latitude, longitude}, ...]
 */

(function () {
  'use strict';

  // ---------------------------------------------------------------------------
  // 1. CONSTANTS
  // ---------------------------------------------------------------------------

  var GEOJSON_URL = '/static/geojson/province/all-provinces.geojson';

  var COLOR_PALETTE = [
    '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
    '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4',
    '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000',
    '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9',
    '#e6beff', '#1abc9c', '#e74c3c', '#3498db', '#2ecc71',
    '#9b59b6', '#f39c12', '#1abc9c', '#d35400', '#c0392b',
    '#7f8c8d', '#2c3e50', '#27ae60', '#8e44ad'
  ];

  var CHOROPLETH_COLORS = ['#feedde', '#fdbe85', '#fd8d3c', '#e6550d', '#a63603'];
  var NO_DATA_COLOR = '#cccccc';

  var DEFAULT_STYLE = {
    weight: 1,
    opacity: 1,
    color: '#999999',
    fillColor: '#f0f0f0',
    fillOpacity: 0.15
  };

  var HIGHLIGHT_STYLE = {
    weight: 3,
    color: '#333333',
    fillOpacity: 0.7
  };

  // ---------------------------------------------------------------------------
  // 2. STATE
  // ---------------------------------------------------------------------------

  var map = null;
  var provinceLayer = null;
  var legend = null;
  var activeLayer = null;
  var provinceLayersMap = {};     // province name (uppercase) → layer
  var provinceColorMap = {};      // province name (uppercase) → assigned color
  var choroplethActive = false;
  var statsMap = {};              // province name (uppercase) → jumlah
  var sortState = { column: -1, direction: 'none' };

  // ---------------------------------------------------------------------------
  // 3. UTILITY FUNCTIONS
  // ---------------------------------------------------------------------------

  /**
   * Show a toast notification at the top-right corner.
   */
  function showToast(message, duration) {
    duration = duration || 4000;
    var toast = document.createElement('div');
    toast.className = 'notification-toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    // Trigger reflow then show
    void toast.offsetWidth;
    toast.classList.add('show');

    setTimeout(function () {
      toast.classList.remove('show');
      setTimeout(function () {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 300);
    }, duration);
  }

  /**
   * Extract the province name from GeoJSON feature properties.
   * Handles various property key formats.
   */
  function getProvinceName(feature) {
    var props = feature.properties || {};
    var name = props.NAME_1 || props.PROPNAME || props.NAME || props.Propinsi || props.name || props.PROVINSI || '';
    return name ? name.toUpperCase() : 'TIDAK DIKETAHUI';
  }

  /**
   * Build popup HTML content for a province.
   */
  function buildPopupContent(name, lat, lng, statValue) {
    var valueSection = '';
    if (statValue !== null && statValue !== undefined) {
      valueSection = '<b>Nilai:</b> <span style="font-size:16px;">' + Number(statValue).toLocaleString('id-ID') + '</span><br>';
    }

    return '<div style="font-family:Arial,sans-serif;font-size:13px;min-width:160px;text-align:center;">' +
      '<h4 style="margin:0 0 5px 0;color:#0d47a1;">' + name + '</h4>' +
      '<hr style="border:0.5px solid #ccc;margin:5px 0;">' +
      '<b>Lat:</b> ' + lat + '<br>' +
      '<b>Lng:</b> ' + lng + '<br>' +
      valueSection +
      '</div>';
  }

  // ---------------------------------------------------------------------------
  // 4. MAP INITIALIZATION
  // ---------------------------------------------------------------------------

  /**
   * Initialize Leaflet map centered on Indonesia.
   */
  function initMap() {
    map = L.map('map').setView([-2.5, 118.0], 5);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Initialize legend control
    legend = L.control({ position: 'bottomright' });
    legend.onAdd = function () {
      var div = L.DomUtil.create('div', 'legend-container');
      div.innerHTML = '<h4>Legend</h4><p>Memuat data...</p>';
      return div;
    };
    legend.addTo(map);

    return map;
  }

  // ---------------------------------------------------------------------------
  // 5. GEOJSON LOADING & COLOR ASSIGNMENT
  // ---------------------------------------------------------------------------

  /**
   * Fetch the combined GeoJSON file and render all provinces.
   * Assigns Color_Palette colors based on feature index.
   */
  function loadProvinces(geojsonUrl) {
    fetch(geojsonUrl)
      .then(function (response) {
        if (!response.ok) throw new Error('GeoJSON fetch failed: ' + response.status);
        return response.json();
      })
      .then(function (geojsonData) {
        provinceLayer = L.geoJSON(geojsonData, {
          style: function (feature) {
            var name = getProvinceName(feature);
            // Store color assignment for later use (highlight/choropleth)
            var idx = geojsonData.features.indexOf(feature);
            var color = COLOR_PALETTE[idx % COLOR_PALETTE.length];
            provinceColorMap[name] = color;

            // Default: plain/neutral style — no color fill until selected
            return {
              fillColor: DEFAULT_STYLE.fillColor,
              weight: DEFAULT_STYLE.weight,
              opacity: DEFAULT_STYLE.opacity,
              color: DEFAULT_STYLE.color,
              fillOpacity: DEFAULT_STYLE.fillOpacity
            };
          },
          onEachFeature: function (feature, layer) {
            var name = getProvinceName(feature);
            provinceLayersMap[name] = layer;

            layer.on({
              click: function (e) {
                selectProvince(name, layer, e.latlng);
              }
            });
          }
        }).addTo(map);

        // Build default legend after loading
        updateLegend('default', null);
      })
      .catch(function (err) {
        console.warn('GeoJSON load error:', err.message);
        showToast('Gagal memuat data peta provinsi. Silakan coba muat ulang halaman.');
      });
  }

  // ---------------------------------------------------------------------------
  // 6. HIGHLIGHT & RESET
  // ---------------------------------------------------------------------------

  /**
   * Highlight a province layer with its assigned palette color.
   * Only the selected province gets colored — all others stay neutral.
   */
  function highlightProvince(layer) {
    if (!layer) return;
    var feature = layer.feature;
    var name = getProvinceName(feature);
    var color = provinceColorMap[name] || '#e6194b';

    layer.setStyle({
      fillColor: color,
      weight: HIGHLIGHT_STYLE.weight,
      color: HIGHLIGHT_STYLE.color,
      fillOpacity: HIGHLIGHT_STYLE.fillOpacity
    });
    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
      layer.bringToFront();
    }
  }

  /**
   * Reset a province layer back to neutral/plain style.
   */
  function resetHighlight(layer) {
    if (!layer) return;
    layer.setStyle({
      fillColor: DEFAULT_STYLE.fillColor,
      weight: DEFAULT_STYLE.weight,
      opacity: DEFAULT_STYLE.opacity,
      color: DEFAULT_STYLE.color,
      fillOpacity: DEFAULT_STYLE.fillOpacity
    });
  }

  /**
   * Single-highlight invariant: only one province highlighted at a time.
   * Handles selecting province by name, triggering highlight, popup, and fitBounds.
   */
  function selectProvince(name, layer, latlng) {
    // Reset previous highlight
    if (activeLayer && activeLayer !== layer) {
      resetHighlight(activeLayer);
    }

    // Highlight the new province
    highlightProvince(layer);
    activeLayer = layer;

    // Fit bounds to the selected province
    map.fitBounds(layer.getBounds());

    // Get lat/lng for popup (from province list or click latlng or centroid)
    var lat = '', lng = '';
    var statValue = null;

    // Try to get data from STAT_DATA
    if (window.STAT_DATA && Array.isArray(window.STAT_DATA)) {
      for (var i = 0; i < window.STAT_DATA.length; i++) {
        if (window.STAT_DATA[i].prov_name && window.STAT_DATA[i].prov_name.toUpperCase() === name) {
          lat = window.STAT_DATA[i].latitude || '';
          lng = window.STAT_DATA[i].longitude || '';
          statValue = window.STAT_DATA[i].jumlah;
          break;
        }
      }
    }

    // Fallback to PROVINCE_LIST
    if (!lat && window.PROVINCE_LIST && Array.isArray(window.PROVINCE_LIST)) {
      for (var j = 0; j < window.PROVINCE_LIST.length; j++) {
        if (window.PROVINCE_LIST[j].name && window.PROVINCE_LIST[j].name.toUpperCase() === name) {
          lat = window.PROVINCE_LIST[j].latitude || '';
          lng = window.PROVINCE_LIST[j].longitude || '';
          break;
        }
      }
    }

    // Fallback to centroid if no data found
    if (!lat && layer.getBounds) {
      var center = layer.getBounds().getCenter();
      lat = center.lat.toFixed(4);
      lng = center.lng.toFixed(4);
    }

    // Show popup
    var popupLatLng = latlng || layer.getBounds().getCenter();
    L.popup()
      .setLatLng(popupLatLng)
      .setContent(buildPopupContent(name, lat, lng, statValue))
      .openOn(map);
  }

  // ---------------------------------------------------------------------------
  // 7. CHOROPLETH
  // ---------------------------------------------------------------------------

  /**
   * Apply choropleth coloring — 5 equal-interval classes, light-to-dark.
   * @param {Array} data - Array of {prov_name, jumlah}
   */
  function applyChoropleth(data) {
    if (!data || data.length === 0 || !provinceLayer) return;

    // Build stats map
    var values = [];
    statsMap = {};
    data.forEach(function (item) {
      if (item.prov_name && item.jumlah !== null && item.jumlah !== undefined) {
        statsMap[item.prov_name.toUpperCase()] = item.jumlah;
        values.push(Number(item.jumlah));
      }
    });

    if (values.length === 0) return;

    var min = Math.min.apply(null, values);
    var max = Math.max.apply(null, values);
    var interval = (max - min) / 5;

    // Avoid zero-interval edge case
    if (interval === 0) interval = 1;

    // Classify function: returns 0–4 class index
    function getClass(value) {
      if (value >= max) return 4;
      var cls = Math.floor((value - min) / interval);
      return Math.min(cls, 4);
    }

    // Apply colors to each province layer
    provinceLayer.eachLayer(function (layer) {
      var feature = layer.feature;
      var name = getProvinceName(feature);
      var value = statsMap[name];

      if (value !== undefined && value !== null) {
        var cls = getClass(Number(value));
        layer.setStyle({
          fillColor: CHOROPLETH_COLORS[cls],
          fillOpacity: 0.6
        });
      } else {
        layer.setStyle({
          fillColor: NO_DATA_COLOR,
          fillOpacity: 0.4
        });
      }
    });

    choroplethActive = true;
    updateLegend('choropleth', { min: min, max: max, interval: interval });
  }

  /**
   * Reset choropleth back to default Color_Palette colors.
   */
  function resetChoropleth() {
    if (!provinceLayer) return;

    provinceLayer.eachLayer(function (layer) {
      layer.setStyle({
        fillColor: DEFAULT_STYLE.fillColor,
        weight: DEFAULT_STYLE.weight,
        opacity: DEFAULT_STYLE.opacity,
        color: DEFAULT_STYLE.color,
        fillOpacity: DEFAULT_STYLE.fillOpacity
      });
    });

    choroplethActive = false;
    activeLayer = null;
    updateLegend('default', null);
  }

  // ---------------------------------------------------------------------------
  // 8. LEGEND
  // ---------------------------------------------------------------------------

  /**
   * Update the legend control.
   * @param {string} mode - 'default' or 'choropleth'
   * @param {object|null} data - For choropleth: {min, max, interval}
   */
  function updateLegend(mode, data) {
    if (!legend || !legend.getContainer) return;
    var container = legend.getContainer();
    if (!container) return;

    var html = '';

    if (mode === 'choropleth' && data) {
      html = '<h4>Legenda Choropleth</h4>';
      for (var i = 0; i < 5; i++) {
        var from = (data.min + i * data.interval).toFixed(1);
        var to = (i === 4)
          ? data.max.toFixed(1)
          : (data.min + (i + 1) * data.interval).toFixed(1);
        html += '<i style="background:' + CHOROPLETH_COLORS[i] + '"></i> ' +
          from + ' &ndash; ' + to + '<br>';
      }
      html += '<i style="background:' + NO_DATA_COLOR + '"></i> Tidak ada data<br>';
    } else {
      // Default mode: no colors applied, show instruction
      html = '<h4>Peta Provinsi</h4>';
      html += '<p style="margin:4px 0;font-size:11px;color:#666;">Klik provinsi di peta atau pilih dari dropdown untuk melihat detail.</p>';
    }

    container.innerHTML = html;
  }

  // ---------------------------------------------------------------------------
  // 9. SELECT2 INTEGRATION
  // ---------------------------------------------------------------------------

  /**
   * Initialize Select2 on #province-selector with search.
   * Falls back to native select if Select2 fails.
   */
  function initProvinceSelector() {
    var selectEl = document.getElementById('province-selector');
    if (!selectEl) return;

    // Populate options from PROVINCE_LIST
    if (window.PROVINCE_LIST && Array.isArray(window.PROVINCE_LIST)) {
      // Sort alphabetically
      var sorted = window.PROVINCE_LIST.slice().sort(function (a, b) {
        return (a.name || '').localeCompare(b.name || '');
      });

      // Clear existing options except placeholder
      selectEl.innerHTML = '<option value="">-- Pilih Provinsi --</option>';
      sorted.forEach(function (prov) {
        var opt = document.createElement('option');
        opt.value = prov.name;
        opt.textContent = prov.name;
        selectEl.appendChild(opt);
      });
    }

    // Try to initialize Select2
    try {
      if (typeof $ !== 'undefined' && $.fn && $.fn.select2) {
        $(selectEl).select2({
          placeholder: '-- Pilih Provinsi --',
          allowClear: true,
          width: '100%'
        });
      } else if (typeof jQuery !== 'undefined' && jQuery.fn && jQuery.fn.select2) {
        jQuery(selectEl).select2({
          placeholder: '-- Pilih Provinsi --',
          allowClear: true,
          width: '100%'
        });
      } else {
        console.warn('Select2 library not found. Using native select.');
      }
    } catch (err) {
      console.warn('Select2 initialization failed, falling back to native select:', err.message);
      showToast('Pencarian provinsi menggunakan dropdown standar.');
    }

    // "Cari" button handler
    var btnCari = document.getElementById('btn-cari');
    if (btnCari) {
      btnCari.addEventListener('click', function (e) {
        e.preventDefault();
        var selectedValue = selectEl.value;

        // Validation: no selection
        var validationMsg = document.getElementById('province-validation');
        if (!selectedValue) {
          if (validationMsg) {
            validationMsg.textContent = 'Silakan pilih provinsi terlebih dahulu.';
            validationMsg.classList.add('visible');
          }
          return;
        }

        // Hide validation message
        if (validationMsg) {
          validationMsg.classList.remove('visible');
        }

        // Find the province layer and select it
        var nameKey = selectedValue.toUpperCase();
        var layer = provinceLayersMap[nameKey];
        if (layer) {
          selectProvince(nameKey, layer, null);
        } else {
          showToast('Batas wilayah provinsi "' + selectedValue + '" tidak ditemukan di peta.');
        }
      });
    }
  }

  // ---------------------------------------------------------------------------
  // 10. TABLE SORT
  // ---------------------------------------------------------------------------

  /**
   * Sort table by clicking column headers.
   * Toggles ascending/descending with arrow indicator.
   */
  function initTableSort() {
    var table = document.querySelector('.tabel-container table');
    if (!table) return;

    var headers = table.querySelectorAll('thead th');
    headers.forEach(function (th, index) {
      // Add sort indicator span
      var indicator = document.createElement('span');
      indicator.className = 'sort-indicator';
      th.appendChild(indicator);

      th.addEventListener('click', function () {
        sortTable(table, index, th, headers);
      });
    });
  }

  /**
   * Sort table rows by the specified column index.
   */
  function sortTable(table, columnIndex, clickedTh, allHeaders) {
    var tbody = table.querySelector('tbody');
    if (!tbody) return;

    var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr:not(.no-data-row):not(.no-results-row)'));
    if (rows.length === 0) return;

    // Determine direction
    var direction;
    if (sortState.column === columnIndex && sortState.direction === 'asc') {
      direction = 'desc';
    } else {
      direction = 'asc';
    }
    sortState.column = columnIndex;
    sortState.direction = direction;

    // Remove sort classes from all headers
    allHeaders.forEach(function (h) {
      h.classList.remove('sorted-asc', 'sorted-desc');
    });

    // Add class to current header
    clickedTh.classList.add(direction === 'asc' ? 'sorted-asc' : 'sorted-desc');

    // Sort rows
    rows.sort(function (rowA, rowB) {
      var cellA = rowA.cells[columnIndex] ? rowA.cells[columnIndex].textContent.trim() : '';
      var cellB = rowB.cells[columnIndex] ? rowB.cells[columnIndex].textContent.trim() : '';

      // Try numeric comparison
      var numA = parseFloat(cellA.replace(/[^\d.-]/g, ''));
      var numB = parseFloat(cellB.replace(/[^\d.-]/g, ''));

      var result;
      if (!isNaN(numA) && !isNaN(numB)) {
        result = numA - numB;
      } else {
        result = cellA.localeCompare(cellB, 'id');
      }

      return direction === 'asc' ? result : -result;
    });

    // Re-append sorted rows
    rows.forEach(function (row) {
      tbody.appendChild(row);
    });
  }

  // ---------------------------------------------------------------------------
  // 11. TABLE FILTER
  // ---------------------------------------------------------------------------

  /**
   * Initialize real-time case-insensitive table filtering on province name.
   */
  function initTableFilter() {
    var filterInput = document.querySelector('.table-search');
    var table = document.querySelector('.tabel-container table');
    if (!filterInput || !table) return;

    filterInput.addEventListener('input', function () {
      filterTable(this.value, table);
    });
  }

  /**
   * Filter table rows by province name (case-insensitive substring match).
   */
  function filterTable(searchText, table) {
    var tbody = table.querySelector('tbody');
    if (!tbody) return;

    var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
    var searchLower = searchText.toLowerCase().trim();
    var visibleCount = 0;

    // Remove any existing no-results row
    var existingNoResults = tbody.querySelector('.no-results-row');
    if (existingNoResults) {
      existingNoResults.parentNode.removeChild(existingNoResults);
    }

    rows.forEach(function (row) {
      if (row.classList.contains('no-data-row') || row.classList.contains('no-results-row')) {
        return;
      }

      // Province name is in column index 1 (after row number)
      var nameCell = row.cells[1];
      if (!nameCell) {
        row.style.display = '';
        return;
      }

      var cellText = nameCell.textContent.toLowerCase();
      if (!searchLower || cellText.indexOf(searchLower) !== -1) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    // Show no-results message if nothing matches
    if (searchLower && visibleCount === 0) {
      var colCount = table.querySelector('thead tr') ? table.querySelector('thead tr').cells.length : 4;
      var noResultsRow = document.createElement('tr');
      noResultsRow.className = 'no-results-row';
      noResultsRow.innerHTML = '<td colspan="' + colCount + '">Tidak ada hasil ditemukan untuk "' + searchText + '"</td>';
      tbody.appendChild(noResultsRow);
    }
  }

  // ---------------------------------------------------------------------------
  // 12. TABLE ROW CLICK → MAP
  // ---------------------------------------------------------------------------

  /**
   * Initialize table row click to fitBounds + highlight the province on map.
   */
  function initTableRowClick() {
    var table = document.querySelector('.tabel-container table');
    if (!table) return;

    var tbody = table.querySelector('tbody');
    if (!tbody) return;

    tbody.addEventListener('click', function (e) {
      var row = e.target.closest('tr');
      if (!row || row.classList.contains('no-data-row') || row.classList.contains('no-results-row')) return;

      // Province name is in column index 1
      var nameCell = row.cells[1];
      if (!nameCell) return;

      var provName = nameCell.textContent.trim().toUpperCase();
      var layer = provinceLayersMap[provName];
      if (layer) {
        selectProvince(provName, layer, null);
      }
    });
  }

  // ---------------------------------------------------------------------------
  // 13. INITIALIZATION (entry point)
  // ---------------------------------------------------------------------------

  function init() {
    // Initialize the map
    initMap();

    // Load provinces from combined GeoJSON
    loadProvinces(GEOJSON_URL);

    // Build stats lookup from window.STAT_DATA
    if (window.STAT_DATA && Array.isArray(window.STAT_DATA)) {
      window.STAT_DATA.forEach(function (item) {
        if (item.prov_name) {
          statsMap[item.prov_name.toUpperCase()] = item.jumlah;
        }
      });

      // Apply choropleth if stat data has jumlah values
      var hasData = window.STAT_DATA.some(function (item) {
        return item.jumlah !== null && item.jumlah !== undefined;
      });

      if (hasData) {
        // Delay slightly to ensure GeoJSON is loaded
        setTimeout(function () {
          applyChoropleth(window.STAT_DATA);
        }, 2000);
      }
    }

    // Initialize Select2 province selector
    initProvinceSelector();

    // Initialize table interactions
    initTableSort();
    initTableFilter();
    initTableRowClick();
  }

  // ---------------------------------------------------------------------------
  // 14. DOM READY
  // ---------------------------------------------------------------------------

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
