
function getSelectedModule(){

  var table = document.getElementById("selectable_table"),rIndex;

  for(var i = 1; i < table.rows.length; i++)
  {
      table.rows[i].onclick = function()
      {

          rIndex = this.cells.item(0).innerHTML;

          $.ajax({

          type: "POST",

          headers: {'content-type': 'application/json'},

          data : JSON.stringify({ "id": rIndex }),

          url: "/module_chooser",

          dataType: "json",

          timeout: 5000,

          success: function (resp) {
            $('#mod_code').html(resp['code']);
            $('#mod_title').html(resp['title']);
            $('#mod_credits').html('<b style="color: rgb(0, 121, 41)">' + resp['credits'] + '</b>' + ' credits');
            $('#mod_lecturer').html(resp['lecturer']);
            $('#class_size').html('Class: <b style="color: rgb(0, 121, 41)">' + resp['size'] + '</b>');
            $('#mod_description').html(resp['description']);
            $('#prereq_table').html('<table class="table"></table>');
            $('#future_table').html('<table class="table"></table>');
            $.each(resp['prerequisites'],function(index, value){
				        $('#prereq_table table').append('<tbody style="font-size: 13.5px;"><tr><td style="display:none;">' + value['prereq_id'] + '</td><td>' +
                value['prereq_code'] + '</td><td>' + value['prereq_title'] + '</td><td>' +value['taken'] +'</td><td>'  + '</td></tr></tbody>');
            });
            $.each(resp['future_choices'],function(index, value){
				        $('#future_table table').append('<tbody style="font-size: 13.5px;"><tr><td style="display:none;">' + value['future_id'] + '</td><td>' + value['future_code'] + '</td><td>' + value['future_title'] + '</td></tr></tbody>');
            });
            $('#mod_url').html('<button id="url_button" type="button" class="btn btn-link">' + '<a href="' + resp['url'] + '">' + 'Catalogue' + '</a>' + '</button>')
            $('#mod_assign_btn').html('<button id="assign_button" onclick="assignModule();" type="submit" class="btn btn-default">Assign</button>')

          },
          error: function (parsedjson, textStatus, errorThrown) {

          console.log("parsedJson: " + JSON.stringify(parsedjson))
          console.log(errorThrown)
          }
        });

      };
  }
}


function assignModule(){

  var module_code = document.getElementById("mod_code").innerHTML;


    $.ajax({

    type: "POST",

    headers: {'content-type': 'application/json'},

    data : JSON.stringify({ "code": module_code }),

    url: "/module_chooser",

    dataType: "json",

    timeout: 5000,

    success: function (resp) {
      $('#assigned_table').load(document.URL +  ' #assigned_table');
      $('.needed_cr').load(' .needed_cr');

      if( resp['err_message'].length) {
        $('#message_alert').html('<div class="alert alert-danger" role="alert">' + resp['err_message'] + '</div>');
      } else if( resp['suc_message'].length) {
        $('#message_alert').html('<div class="alert alert-success" role="alert">' + resp['suc_message'] + resp['code'] + ' ' + resp['title'] + '</div>');
      } else if( resp['info_message'].length) {
        $('#message_alert').html('<div class="alert alert-info" role="alert">' + resp['info_message'] + resp['code'] + ' ' + resp['title'] + '</div>');
      }


    },
    error: function (parsedjson, textStatus, errorThrown) {

    console.log("parsedJson: " + JSON.stringify(parsedjson))
    console.log(errorThrown)
    }
  });
}

function searchTable() {
  var input, filter, table, tr, td, i;
  input = document.getElementById("search");
  filter = input.value.toUpperCase();
  table = document.getElementById("selectable_table");
  tr = table.getElementsByTagName("tr");
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[1];
    if (td) {
      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
        tr[i].classList.add('d-flex')
      } else {
        tr[i].classList.remove('d-flex')
        tr[i].style.display = "none";
      }
    }
  }
}

function sortTable() {
  var table = $('#selectable_table');

    $('#module, #year, #semester, #credits_mod')
        .each(function(){

            var th = $(this),
                thIndex = th.index(),
                inverse = false;

            th.click(function(){

                table.find('td').filter(function(){

                    return $(this).index() === thIndex;

                }).sortElements(function(a, b){

                    return $.text([a]).toUpperCase() > $.text([b]).toUpperCase() ?
                        inverse ? -1 : 1
                        : inverse ? 1 : -1;

                }, function(){

                    // parentNode is the element we want to move
                    return this.parentNode;

                });

                inverse = !inverse;

            });

        });
}

function sortAssignedTable() {
  var table = $('#assigned_table');

    $('#assigned_module, #assigned_year, #assigned_semester, #assigned_credits_mod')
        .each(function(){

            var th = $(this),
                thIndex = th.index(),
                inverse = false;

            th.click(function(){

                table.find('td').filter(function(){

                    return $(this).index() === thIndex;

                }).sortElements(function(a, b){

                    return $.text([a]).toUpperCase() > $.text([b]).toUpperCase() ?
                        inverse ? -1 : 1
                        : inverse ? 1 : -1;

                }, function(){

                    // parentNode is the element we want to move
                    return this.parentNode;

                });

                inverse = !inverse;

            });

        });
}
