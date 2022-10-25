// const month_list = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'];
const month_list_pad = ['Января','Февраля','Марта','Апреля','Мая','Июня','Июля','Августа','Сентября','Октября','Ноября','Декабря'];
var today_date_cont = document.querySelector('.today-is-heading');
var today_is = new Date();
var make_today = function() {
    today_is_cont = today_is.getDate() + ' ' + month_list_pad[today_is.getMonth()];
    today_date_cont.textContent = 'Сегодня, ' + today_is_cont;
}
make_today();


var Cal = function(divId) {
    this.divId = divId;
    this.DaysOfWeek = [
      'Пн',
      'Вт',
      'Ср',
      'Чт',
      'Пт',
      'Сб',
      'Вс'
    ];
    this.Months =['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
    var d = new Date();
    this.currMonth = d.getMonth();
    window.crMonth = this.currMonth;
    this.currYear = d.getFullYear();
    this.currDay = d.getDate();
  };
  Cal.prototype.nextMonth = function() {
    if ( this.currMonth == 11 ) {
      this.currMonth = 0;
      window.crMonth = this.currMonth;
      this.currYear = this.currYear + 1;
    }
    else {
      this.currMonth = this.currMonth + 1;
      window.crMonth = this.currMonth;
    }
    this.showcurr();
  };
  Cal.prototype.previousMonth = function() {
    if ( this.currMonth == 0 ) {
      this.currMonth = 11;
      window.crMonth = this.currMonth;
      this.currYear = this.currYear - 1;
    }
    else {
      this.currMonth = this.currMonth - 1;
      window.crMonth = this.currMonth;
    }
    this.showcurr();
  };
  Cal.prototype.showcurr = function() {
    this.showMonth(this.currYear, this.currMonth);
  };
  Cal.prototype.showMonth = function(y, m) {
    var d = new Date()
    , firstDayOfMonth = new Date(y, m, 7).getDay()
    , lastDateOfMonth =  new Date(y, m+1, 0).getDate()
    , lastDayOfLastMonth = m == 0 ? new Date(y-1, 11, 0).getDate() : new Date(y, m, 0).getDate();
    var html = '<table>';
    html += '<thead><tr>';
    html += '<td class="month-year" colspan="7">' + this.Months[m] + ' ' + y + '</td>';
    html += '</tr></thead>';
    html += '<tr class="days">';
    for(var i=0; i < this.DaysOfWeek.length;i++) {
      html += '<td>' + this.DaysOfWeek[i] + '</td>';
    }
    html += '</tr>';
    var i=1;
    do {
      var dow = new Date(y, m, i).getDay();
      if ( dow == 1 ) {
        html += '<tr>';
      }
      else if ( i == 1 ) {
        html += '<tr>';
        var k = lastDayOfLastMonth - firstDayOfMonth+1;
        for(var j=0; j < firstDayOfMonth; j++) {
          html += '<td class="not-current">' + k + '</td>';
          k++;
        }
      }
      var chk = new Date();
      var chkY = chk.getFullYear();
      var chkM = chk.getMonth();
      if (chkY == this.currYear && chkM == this.currMonth && i == this.currDay) {
        html += '<td class="today" id="cal-days' + i + '">' + i + '</td>';
      } else {
        html += '<td class="normal" id="cal-days' + i + '">' + i + '</td>';
      }
      if ( dow == 0 ) {
        html += '</tr>';
      }
      else if ( i == lastDateOfMonth ) {
        var k=1;
        for(dow; dow < 7; dow++) {
          html += '<td class="not-current">' + k + '</td>';
          k++;
        }
      }
      i++;
    }while(i <= lastDateOfMonth);
    html += '</table>';
    document.getElementById(this.divId).innerHTML = html;
  };
  window.onload = function() {
    var c = new Cal("divCal");			
    c.showcurr();
    getId('btnNext').onclick = function() {
        c.nextMonth();
        if (window.crMonth === today_is.getMonth()){
            totoday(1);
            make_today();
        } else {
            totoday(0);
        }
    };
    getId('btnPrev').onclick = function() {
        c.previousMonth();
        if (window.crMonth === today_is.getMonth()){
            totoday(1);
            make_today();
        } else {
            totoday(0);
        }
    };
    var totoday = function(x) {

        for (var i=1; i < 32; i++)
        {
            let caldayscur = 'cal-days' + i;
            let crDay = i;
            getId(caldayscur).onclick = function() {
                if (x === 1)
                {
                    document.querySelector('.today').classList.add('normal');
                    document.querySelector('.today').classList.remove('today');
                } else {
                    x = 1
                }
                getId(caldayscur).classList.remove('normal');
                getId(caldayscur).classList.add('today');
                today_date_cont.textContent = crDay + ' ' + month_list_pad[window.crMonth];
                console.log(crDay, today_is.getDate())
                if (window.crMonth === today_is.getMonth() && crDay === today_is.getDate()) {
                    make_today();
                }
            }
        }
    }
    totoday(1);
  }
  function getId(id) {
    return document.getElementById(id);
  };