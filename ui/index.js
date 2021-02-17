var app = null;


var registered_functions = []
var loaded_dir = {}
var directing_to_path = null;
var loading = true;

function initial_path() {
  // Default current path to '.'
  var default_path = "."
  // Check to see if there was a privided starting path
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('b64path')) {
    default_path = urlParams.get('b64path')
  }
  return default_path
}

function requestReturn(data) {
  console.log("Request returned.")
  current_path = directing_to_path
  loaded_dir = JSON.parse(data)
  for (var i=0; i<registered_functions.length; i++) {
    registered_functions[i](loaded_dir)
  }
  loading = false
}

function handleError(data) {
  console.log(data)
  alert(data.status + ": " + data.statusText)
}

function makeRequest(path) {
  encoded = btoa(path)
  resultingUrl = 'http://127.0.0.1:5000/ls?b64path=' + encoded
  console.log("Making API request: " + resultingUrl)
  directing_to_path = path
  loading = true
  // make API request
  $.ajax({
    url: resultingUrl,
    type: 'GET',
    success: requestReturn,
    error: handleError
  })
}



Vue.component('lsrow', {
    template: `
    <tr :class="getClass" v-on:click="selected">
      <td> <img v-if="isDir" src="dir_icon.ico" class="dir" /> </td>
      <td class="nameColumn"> {{ this.row.Name }} </td>
      <td class="size"> {{ this.row.Size }} </td>
      <td class="modified"> {{ this.row["Last Modified"] }} </td>
    </tr>
    `,
    data() {
        return {}
    },
    methods: {
      selected() {
        if (this.isDir) {
          makeRequest(this.row.path)
        }
      }
    },
    computed: {
      isDir: function() {
        if (this.row.Type === 'DIR') {
          return true
        }
        return false
      },
      getClass: function() {
        return this.row.Type.toLowerCase()
      }
    },
    props: {
      row: {
        type: Object,
        required:true
      }
    }
})

Vue.component('lstable', {
    template: `
        <table>
        <tr>
          <th></th>
          <th>Name</th>
          <th>Size</th>
          <th>Last Modified</th>
        </tr>
        <lsrow v-for="r in getRows" :row="r" />
        </table>
    `,
    data() {
        console.log("Registering table")
        registered_functions.push(this.save_data)
        makeRequest(initial_path())
        return {rows:[]}
    },
    methods: {
      save_data: function(data) {
        this.rows = data["contents"]
      }
    },
    props: {},
    computed: {
      getRows() {
        return this.rows
      }
    }
})

Vue.component('buttoncomp', {
  template: `
    <div class="upArrow" v-on:click="callback">
      <div ><img :src="img" class="upArrow" /></div>
      <div class="upText"><span>{{ text }}</span></div>
    </div>
  `,
  props: {
    callback: {
      required: true
    },
    text: {
      type: String,
      required: true
    },
    img: {
      type: String
    }
  }
})

Vue.component('lshead', {
  template: `
    <div>
      <input type="text" id="searchbox" class="searchbox" @keyup.enter="goTo" @keyup="checkDiff">
      <buttoncomp :callback="goUpDir" text="Up Directory" img="up_dir.png" />
      <buttoncomp :callback="goTo" text="Go to Path" img="dir_icon.png" v-if="diff" />
    </div>
  `,
  data() {
    console.log("Registering searchbox")
    registered_functions.push(this.save_data)
    return {originalPath:"",
            diff: false}
  },
  methods: {
    goUpDir: function() {
      upDir = loaded_dir["path"]

      if (upDir.substr(upDir.length - 1) != "/") {
        upDir += "/"
      }
      upDir += ".."
      makeRequest(upDir)
    },
    save_data: function(data) {
      this.originalPath = data.path
      document.getElementById("searchbox").value = this.originalPath
      this.checkDiff()
    },
    goTo: function() {
      makeRequest(document.getElementById("searchbox").value)
    },
    checkDiff: function() {
      this.diff = (this.originalPath != document.getElementById("searchbox").value)
    }
  },
  computed: {
    getPath() {
      console.log(loaded_dir);
      return this.path
    }
  }
})

Vue.component('dirpage', {
  template: `
    <div>
    <lshead />

    <lstable />
    </div>
  `
})

app = new Vue({
  el: '#app',
  data() {
    console.log("App has loaded")
    return {}
  }
})
