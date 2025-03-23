;(function () {
	
	'use strict';



	// iPad and iPod detection	
	var isiPad = function(){
		return (navigator.platform.indexOf("iPad") != -1);
	};

	var isiPhone = function(){
	    return (
			(navigator.platform.indexOf("iPhone") != -1) || 
			(navigator.platform.indexOf("iPod") != -1)
	    );
	};

	// Main Menu Superfish
	var mainMenu = function() {

		$('#fh5co-primary-menu').superfish({
			delay: 0,
			animation: {
				opacity: 'show'
			},
			speed: 'fast',
			cssArrows: true,
			disableHI: true
		});

	};

	// Parallax
	var parallax = function() {
		$(window).stellar();
	};


	// Offcanvas and cloning of the main menu
	var offcanvas = function() {

		var $clone = $('#fh5co-menu-wrap').clone();
		$clone.attr({
			'id' : 'offcanvas-menu'
		});
		$clone.find('> ul').attr({
			'class' : '',
			'id' : ''
		});

		$('#fh5co-page').prepend($clone);

		// click the burger
		$('.js-fh5co-nav-toggle').on('click', function(){

			if ( $('body').hasClass('fh5co-offcanvas') ) {
				$('body').removeClass('fh5co-offcanvas');
			} else {
				$('body').addClass('fh5co-offcanvas');
			}
			

		});

		$('#offcanvas-menu').css('height', $(window).height());

		$(window).resize(function(){
			var w = $(window);


			$('#offcanvas-menu').css('height', w.height());

			if ( w.width() > 769 ) {
				if ( $('body').hasClass('fh5co-offcanvas') ) {
					$('body').removeClass('fh5co-offcanvas');
				}
			}

		});	

	}

	

	// Click outside of the Mobile Menu
	var mobileMenuOutsideClick = function() {
		$(document).click(function (e) {
	    var container = $("#offcanvas-menu, .js-fh5co-nav-toggle");
	    if (!container.is(e.target) && container.has(e.target).length === 0) {
	      if ( $('body').hasClass('fh5co-offcanvas') ) {
				$('body').removeClass('fh5co-offcanvas');
			}
	    }
		});
	};


	// Animations

	var contentWayPoint = function() {
		var i = 0;
		$('.animate-box').waypoint( function( direction ) {

			if( direction === 'down' && !$(this.element).hasClass('animated') ) {
				
				i++;

				$(this.element).addClass('item-animate');
				setTimeout(function(){

					$('body .animate-box.item-animate').each(function(k){
						var el = $(this);
						setTimeout( function () {
							el.addClass('fadeInUp animated');
							el.removeClass('item-animate');
						},  k * 50, 'easeInOutExpo' );
					});
					
				}, 100);
				
			}

		} , { offset: '85%' } );
	};
	
	var stickyBanner = function() {
		var $stickyElement = $('.sticky-banner');
		var sticky;
		if ($stickyElement.length) {
		  sticky = new Waypoint.Sticky({
		      element: $stickyElement[0],
		      offset: 0
		  })
		}
	}; 

	// Document on load.
	$(function(){
		mainMenu();
		parallax();
		offcanvas();
		mobileMenuOutsideClick();
		contentWayPoint();
		stickyBanner();
	});

	// Login form handling
	document.addEventListener('DOMContentLoaded', function() {
		// Donor Login Form
		const donorLoginForm = document.getElementById('donor-login-form');
		if (donorLoginForm) {
			donorLoginForm.addEventListener('submit', function(e) {
				e.preventDefault();
				
				const email = document.getElementById('donor-email').value;
				const password = document.getElementById('donor-password').value;
				
				fetch('/api/donor/login/', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						email: email,
						password: password
					}),
					credentials: 'include'
				})
				.then(response => response.json())
				.then(data => {
					if (data.success) {
						// Store user info in localStorage
						localStorage.setItem('userEmail', data.email);
						localStorage.setItem('userId', data.user_id);
						
						// Redirect to donor dashboard
						window.location.href = '/donsubmit/';
					} else {
						// Show error message
						alert(data.message);
					}
				})
				.catch(error => {
					console.error('Error:', error);
					alert('An error occurred. Please try again.');
				});
			});
		}

		// Organization Login Form
		const orgLoginForm = document.getElementById('org-login-form');
		if (orgLoginForm) {
			orgLoginForm.addEventListener('submit', function(e) {
				e.preventDefault();
				
				const email = document.getElementById('org-email').value;
				const password = document.getElementById('org-password').value;
				
				fetch('/api/organization/login/', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						email: email,
						password: password
					}),
					credentials: 'include'
				})
				.then(response => response.json())
				.then(data => {
					if (data.success) {
						// Store user info in localStorage
						localStorage.setItem('userEmail', data.email);
						localStorage.setItem('userId', data.user_id);
						
						// Redirect to organization dashboard
						window.location.href = '/orgsubmit/';
					} else {
						// Show error message
						alert(data.message);
					}
				})
				.catch(error => {
					console.error('Error:', error);
					alert('An error occurred. Please try again.');
				});
			});
		}
	});

}());