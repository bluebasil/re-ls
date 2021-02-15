var app = null;


var registered_functions = []
var loaded_dir = {}
var current_path = "."
var directing_to_path = null;
var loading = true;

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
  console.log("Makeing API request...")
  encoded = btoa(path)
  resultingUrl = 'http://127.0.0.1:5000/ls?b64path=' + encoded
  console.log(resultingUrl)
  directing_to_path = path
  loading = true
  // jQuery.get(resultingUrl, "", requestReturn, "text").error(handleError)
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
    // template: `
    //   <div :class="getClass" v-on:click="selected">
    //     <span class="cell icon"> <img v-if="isDir" src="dir_icon.ico" class="dir" /> </span>
    //     <span class="cell name"> {{ this.row.Name }} </span>
    //     <span class="cell modified"> {{ this.row["Last Modified"] }} </span>
    //     <span class="cell size"> {{ this.row.Size }}  </span>
    //   </div
    // `,
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
    // template: `
    //   <div class="table">
    //     <lsrow v-for="r in getRows" :row="r" />
    //   </div>
    // `,
    data() {
        //console.log("data loading...")
        //Query.get('http://127.0.0.1:5000/ls?b64path=Li4vLi4=', "", this.save_data, "text")
        console.log("Registering table")
        registered_functions.push(this.save_data)
        makeRequest(".")
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

//

Vue.component('uparrow', {
  template: `
    <div class="upArrow" v-on:click="goUpDir">
    <div ><img src="up_dir.png" v-on:click="this.goUpDir" class="upArrow" /></div>
    <div class="upText"><span>Up Directory</span></div>
    </div>
  `,
  methods: {
    goUpDir: function() {
      console.log(loaded_dir)
      upDir = loaded_dir["path"]
      console.log(upDir)

      if (upDir.substr(upDir.length - 1) != "/") {
        upDir += "/"
      }
      upDir += ".."
      makeRequest(upDir)
    }
  }
})

Vue.component('searchbox', {
  template: `
    <div>
      <input type="text" :value="getPath" class="searchbox">

    </div>
  `,
  data() {
    console.log("Registering searchbox")
    registered_functions.push(this.save_data)
    return {path:""}
  },
  methods: {
    save_data: function(data) {
      this.path = data.path
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
    <searchbox />
    <uparrow />

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
