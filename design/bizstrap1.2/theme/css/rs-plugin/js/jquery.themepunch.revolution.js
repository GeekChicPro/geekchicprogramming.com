/**************************************************************************
 * jquery.themepunch.revolution.js - jQuery Plugin for kenburn Slider
 * @version: 1.3.2 (05.09.2012)
 * @requires jQuery v1.4 or later
 * @author Krisztian Horvath
**************************************************************************/





(function($,undefined){




	////////////////////////////////////////
	// THE REVOLUTION PLUGIN STARTS HERE //
	///////////////////////////////////////

	$.fn.extend({


		// OUR PLUGIN HERE :)
		revolution: function(options) {



		////////////////////////////////
		// SET DEFAULT VALUES OF ITEM //
		////////////////////////////////
		var defaults = {
			delay:9000,
			startheight:490,
			startwidth:890,

			hideThumbs:200,

			thumbWidth:100,							// Thumb With and Height and Amount (only if navigation Tyope set to thumb !)
			thumbHeight:50,
			thumbAmount:5,

			navigationType:"both",					//bullet, thumb, none, both		(No Thumbs In FullWidth Version !)
			navigationArrows:"nexttobullets",		//nexttobullets, verticalcentered, none
			navigationStyle:"round",				//round,square,navbar

			touchenabled:"on",						// Enable Swipe Function : on/off
			onHoverStop:"on",						// Stop Banner Timet at Hover on Slide on/off

			navOffsetHorizontal:0,
			navOffsetVertical:20,

			shadow:1,

			stopLoop:"off"
		};

			options = $.extend({}, $.fn.revolution.defaults, options);




			return this.each(function() {

				var opt=options;

				// CATCH THE CONTAINER
				var container=$(this);

				 // LOAD THE YOUTUBE API IF NECESSARY
				 
				container.find('.caption iframe').each(function() {
					try {
							if ($(this).attr('src').indexOf('you')>0) {
								
								var s = document.createElement("script");
								s.src = "http://www.youtube.com/player_api"; /* Load Player API*/
								var before = document.getElementsByTagName("script")[0];
								before.parentNode.insertBefore(s, before);
							}
						} catch(e) {}
				});



				 // LOAD THE VIMEO API
				 container.find('.caption iframe').each(function() {
					try{
							if ($(this).attr('src').indexOf('vim')>0) {
							
								var f = document.createElement("script");
								f.src = "http://a.vimeocdn.com/js/froogaloop2.min.js"; /* Load Player API*/
								var before = document.getElementsByTagName("script")[0];
								before.parentNode.insertBefore(f, before);
							}
						} catch(e) {}
				});



				// CREATE SOME DEFAULT OPTIONS FOR LATER
				opt.slots=4;
				opt.act=-1;
				opt.next=0;
				opt.origcd=opt.delay;

				// CHECK IF FIREFOX 13 IS ON WAY.. IT HAS A STRANGE BUG, CSS ANIMATE SHOULD NOT BE USED
				opt.firefox13 = ($.browser.mozilla)  && (parseInt($.browser.version,0)==13 ||  parseInt($.browser.version,0)==14);
				opt.ie = $.browser.msie && parseInt($.browser.version,0)<9;




				// BASIC OFFSET POSITIONS OF THE BULLETS
				if (opt.navOffsetHorizontal==undefined) opt.navOffsetHorizontal=0;
				if (opt.navOffsetVertical==undefined) opt.navOffsetVertical=0;

				// SHORTWAY USAGE OF OFFSETS
				opt.navOH = opt.navOffsetHorizontal;
				opt.navOV = opt.navOffsetVertical;



				container.append('<div class="tp-loader"></div>');

				// RESET THE TIMER
				var bt=container.find('.tp-bannertimer');
				if (bt.length>0) {
					bt.css({'width':'0%'});
				};


				// WE NEED TO ADD A BASIC CLASS FOR SETTINGS.CSS
				container.addClass("tp-simpleresponsive");
				opt.container=container;

				//if (container.height()==0) container.height(opt.startheight);

				// AMOUNT OF THE SLIDES
				opt.slideamount = container.find('ul:first li').length;

				// A BASIC GRID MUST BE DEFINED. IF NO DEFAULT GRID EXIST THAN WE NEED A DEFAULT VALUE, ACTUAL SIZE OF CONAINER
				if (opt.startwidth==undefined || opt.startwidth==0) opt.startwidth=container.width();
				if (opt.startheight==undefined || opt.startheight==0) opt.startheight=container.height();

				// OPT WIDTH && HEIGHT SHOULD BE SET
				opt.width=container.width();
				opt.height=container.height();

				// DEFAULT DEPENDECIES
				opt.bw = opt.startwidth / container.width();
				opt.bh = opt.startheight / container.height();

				// IF THE ITEM ALREADY IN A RESIZED FORM
				if (opt.width!=opt.startwidth) {

					opt.height = Math.round(opt.startheight * (opt.width/opt.startwidth));
					container.height(opt.height);

				}

				// LETS SEE IF THERE IS ANY SHADOW
				if (opt.shadow!=0) {
					container.parent().append('<div class="tp-bannershadow tp-shadow'+opt.shadow+'"></div>');

					container.parent().find('.tp-bannershadow').css({'width':opt.width});
				}



				// IF IMAGES HAS BEEN LOADED
				container.waitForImages(function() {
						// PREPARE THE SLIDES
						prepareSlides(container,opt);

						// CREATE BULLETS
						createBullets(container,opt);
						createThumbs(container,opt);
						createArrows(container,opt);
						swipeAction(container,opt);

						if (opt.hideThumbs>0) hideThumbs(container,opt);

						container.waitForImages(function() {
							// START THE FIRST SLIDE
							container.find('.tp-loader').fadeOut(400);
							setTimeout(function() {
								swapSlide(container,opt);
								// START COUNTDOWN
								countDown(container,opt);
							},1000);
						});


				});


				// IF RESIZED, NEED TO STOP ACTUAL TRANSITION AND RESIZE ACTUAL IMAGES
				$(window).resize(function() {

					if (container.outerWidth(true)!=opt.width) {

						containerResized(container,opt);

					}
				});
			})
		}

})

		//////////////////////////
		//	CONTAINER RESIZED	//
		/////////////////////////
		function containerResized(container,opt) {


			container.find('.defaultimg').each(function(i) {

						setSize($(this),opt);

						opt.height = Math.round(opt.startheight * (opt.width/opt.startwidth));
						container.height(opt.height);

						setSize($(this),opt);

						try{
							container.parent().find('.tp-bannershadow').css({'width':opt.width});
						} catch(e) {}

						var actsh = container.find('li:eq('+opt.act+') .slotholder');
						var nextsh = container.find('li:eq('+opt.next+') .slotholder');
						removeSlots(container);
						nextsh.find('.defaultimg').css({'opacity':0});
						actsh.find('.defaultimg').css({'opacity':1});

						setCaptionPositions(container,opt);

						var nextli = container.find('li:eq('+opt.next+')');
						container.find('.caption').each(function() { $(this).stop(true,true);});
						animateTheCaptions(nextli, opt);

						restartBannerTimer(opt,container);

				});
		}



		////////////////////////////////
		//	RESTART THE BANNER TIMER //
		//////////////////////////////
		function restartBannerTimer(opt,container) {
						opt.cd=0;
						if (opt.videoplaying !=true) {
							var bt=	container.find('.tp-bannertimer');
								if (bt.length>0) {
									bt.stop();
									bt.css({'width':'0%'});
									bt.animate({'width':"100%"},{duration:(opt.delay-100),queue:false, easing:"linear"});
								}
							clearTimeout(opt.thumbtimer);
							opt.thumbtimer = setTimeout(function() {
								moveSelectedThumb(container);
								setBulPos(container,opt);
							},200);
						}
		}

		function callingNewSlide(opt,container) {
						opt.cd=0;
						swapSlide(container,opt);

						// STOP TIMER AND RESCALE IT
							var bt=	container.find('.tp-bannertimer');
							if (bt.length>0) {
								bt.stop();
								bt.css({'width':'0%'});
								bt.animate({'width':"100%"},{duration:(opt.delay-100),queue:false, easing:"linear"});
							}
		}



		////////////////////////////////
		//	-	CREATE THE BULLETS -  //
		////////////////////////////////
		function createThumbs(container,opt) {

			var cap=container.parent();

			if (opt.navigationType=="thumb" || opt.navsecond=="both") {
						cap.append('<div class="tp-bullets tp-thumbs '+opt.navigationStyle+'"><div class="tp-mask"><div class="tp-thumbcontainer"></div></div></div>');
			}
			var bullets = cap.find('.tp-bullets.tp-thumbs .tp-mask .tp-thumbcontainer');
			var bup = bullets.parent();

			bup.width(opt.thumbWidth*opt.thumbAmount);
			bup.height(opt.thumbHeight);
			bup.parent().width(opt.thumbWidth*opt.thumbAmount);
			bup.parent().height(opt.thumbHeight);

			container.find('ul:first li').each(function(i) {
							var li= container.find("ul:first li:eq("+i+")");
							if (li.data('thumb') !=undefined)
								var src= li.data('thumb')
							else
								var src=li.find("img:first").attr('src');
							bullets.append('<div class="bullet thumb"><img src="'+src+'"></div>');
							var bullet= bullets.find('.bullet:first');
				});
			bullets.append('<div style="clear:both"></div>');
			var minwidth=1000;


			// ADD THE BULLET CLICK FUNCTION HERE
			bullets.find('.bullet').each(function(i) {
				var bul = $(this);

				if (i==opt.slideamount-1) bul.addClass('last');
				if (i==0) bul.addClass('first');
				bul.width(opt.thumbWidth);
				bul.height(opt.thumbHeight);
				if (minwidth>bul.outerWidth(true)) minwidth=bul.outerWidth(true);

				bul.click(function() {
					if (opt.transition==0 && bul.index() != opt.act) {
						opt.next = bul.index();
						callingNewSlide(opt,container);
					}
				});
			});


			var max=minwidth*container.find('ul:first li').length;
			var thumbconwidth=bullets.parent().width();
			opt.thumbWidth = minwidth;



				////////////////////////
				// SLIDE TO POSITION  //
				////////////////////////
				if (thumbconwidth<max) {
					$(document).mousemove(function(e) {
						$('body').data('mousex',e.pageX);
					});



					// ON MOUSE MOVE ON THE THUMBNAILS EVERYTHING SHOULD MOVE :)

					bullets.parent().mouseenter(function() {
							var $this=$(this);
							$this.addClass("over");
							var offset = $this.offset();
							var x = $('body').data('mousex')-offset.left;
							var thumbconwidth=$this.width();
							var minwidth=$this.find('.bullet:first').outerWidth(true);
							var max=minwidth*container.find('ul:first li').length;
							var diff=(max- thumbconwidth)+15;
							var steps = diff / thumbconwidth;
							x=x-30;
							//if (x<30) x=0;
							//if (x>thumbconwidth-30) x=thumbconwidth;

							//ANIMATE TO POSITION
							var pos=(0-((x)*steps));
							if (pos>0) pos =0;
							if (pos<0-max+thumbconwidth) pos=0-max+thumbconwidth;
							moveThumbSliderToPosition($this,pos,200);
					});

					bullets.parent().mousemove(function() {

									var $this=$(this);

									//if (!$this.hasClass("over")) {
											var offset = $this.offset();
											var x = $('body').data('mousex')-offset.left;
											var thumbconwidth=$this.width();
											var minwidth=$this.find('.bullet:first').outerWidth(true);
											var max=minwidth*container.find('ul:first li').length;
											var diff=(max- thumbconwidth)+15;
											var steps = diff / thumbconwidth;
											x=x-30;
											//if (x<30) x=0;
											//if (x>thumbconwidth-30) x=thumbconwidth;

											//ANIMATE TO POSITION
											var pos=(0-((x)*steps));
											if (pos>0) pos =0;
											if (pos<0-max+thumbconwidth) pos=0-max+thumbconwidth;
											moveThumbSliderToPosition($this,pos,0);
									//} else {
										//$this.removeClass("over");
									//}

					});

					bullets.parent().mouseleave(function() {
									var $this=$(this);
									$this.removeClass("over");
									moveSelectedThumb(container);
					});
				}
		}


		///////////////////////////////
		//	SelectedThumbInPosition //
		//////////////////////////////
		function moveSelectedThumb(container) {

									var bullets=container.parent().find('.tp-bullets.tp-thumbs .tp-mask .tp-thumbcontainer');
									var $this=bullets.parent();
									var offset = $this.offset();
									var minwidth=$this.find('.bullet:first').outerWidth(true);

									var x = $this.find('.bullet.selected').index() * minwidth;
									var thumbconwidth=$this.width();
									var minwidth=$this.find('.bullet:first').outerWidth(true);
									var max=minwidth*container.find('ul:first li').length;
									var diff=(max- thumbconwidth);
									var steps = diff / thumbconwidth;

									//ANIMATE TO POSITION
									var pos=0-x;

									if (pos>0) pos =0;
									if (pos<0-max+thumbconwidth) pos=0-max+thumbconwidth;
									if (!$this.hasClass("over")) {
										moveThumbSliderToPosition($this,pos,200);
									}
		}


		////////////////////////////////////
		//	MOVE THUMB SLIDER TO POSITION //
		///////////////////////////////////
		function moveThumbSliderToPosition($this,pos,speed) {
			$this.stop();
			$this.find('.tp-thumbcontainer').animate({'left':pos+'px'},{duration:speed,queue:false});
		}



		////////////////////////////////
		//	-	CREATE THE BULLETS -  //
		////////////////////////////////
		function createBullets(container,opt) {

			if (opt.navigationType=="bullet"  || opt.navigationType=="both") {
						container.parent().append('<div class="tp-bullets simplebullets '+opt.navigationStyle+'"></div>');
			}


			var bullets = container.parent().find('.tp-bullets');

			container.find('ul:first li').each(function(i) {
							var src=container.find("ul:first li:eq("+i+") img:first").attr('src');
							bullets.append('<div class="bullet"></div>');
							var bullet= bullets.find('.bullet:first');
				});



			// ADD THE BULLET CLICK FUNCTION HERE
			bullets.find('.bullet').each(function(i) {
				var bul = $(this);
				if (i==opt.slideamount-1) bul.addClass('last');
				if (i==0) bul.addClass('first');

				bul.click(function() {
					if (opt.transition==0 && bul.index() != opt.act) {
						opt.next = bul.index();
						callingNewSlide(opt,container);
					}
				});

			});

			bullets.append('<div style="clear:both"></div>');
			setBulPos(container,opt);

			$('#unvisible_button').click(function() {

				opt.navigationArrows=$('.select_navarrows .selected').data('value');
				opt.navigationType=$('.select_navigationtype .selected').data('value');
				opt.hideThumbs=$('.select_navshow .selected').data('value');
				container.data('hidethumbs',opt.hideThumbs);

				var bhd = $('.select_bhposition .dragger');
				opt.navOffsetHorizontal = Math.round(((bhd.data('max') - bhd.data('min')) *  (bhd.position().left/410)) +  bhd.data('min'));

				var bvd = $('.select_bvposition .dragger');
				opt.navOffsetVertical = Math.round(((bvd.data('max') - bvd.data('min')) *  (bvd.position().left/410)) +  bvd.data('min'));

				var btr = $('.select_slidetime .dragger');
				opt.delay2 = Math.round((((btr.data('max') - btr.data('min')) *  (btr.position().left/410)) +  btr.data('min'))*1000);

				if (opt.delay2!=opt.delay) {
							opt.delay=opt.delay2;
							opt.origcd = opt.delay;
							opt.cd=0;
							var bt=	container.find('.tp-bannertimer');
							if (bt.length>0) {
								bt.stop();
								bt.css({'width':'0%'});
								bt.animate({'width':"100%"},{duration:(opt.delay-100),queue:false, easing:"linear"});
							}
				}

				opt.onHoverStop = $('.select_hovers .selected').data('value');

				setBulPos(container,opt);
				setTimeout(function() {
					setBulPos(container,opt);
				},100);
			});

		}

		//////////////////////
		//	CREATE ARROWS	//
		/////////////////////
		function createArrows(container,opt) {

						var bullets = container.find('.tp-bullets');

						if (opt.navigationArrow!="none") container.parent().append('<div class="tp-leftarrow tparrows '+opt.navigationStyle+'"></div>');
						if (opt.navigationArrow!="none") container.parent().append('<div class="tp-rightarrow tparrows '+opt.navigationStyle+'"></div>');




						// 	THE LEFT / RIGHT BUTTON CLICK !	 //
						container.parent().find('.tp-rightarrow').click(function() {

							if (opt.transition==0) {
									opt.next = opt.next+1;
									if (opt.next == opt.slideamount) opt.next=0;
									callingNewSlide(opt,container);
							}
						});

						container.parent().find('.tp-leftarrow').click(function() {
							if (opt.transition==0) {
									opt.next = opt.next-1;
									if (opt.next < 0) opt.next=opt.slideamount-1;
									callingNewSlide(opt,container);
							}
						});

						setBulPos(container,opt);
		}

		////////////////////////////
		// SET THE SWIPE FUNCTION //
		////////////////////////////
		function swipeAction(container,opt) {
			// TOUCH ENABLED SCROLL

				if (opt.touchenabled=="on")
						container.swipe( {data:container,
										swipeRight:function()
												{

													if (opt.transition==0) {
															opt.next = opt.next-1;
															if (opt.next < 0) opt.next=opt.slideamount-1;
															callingNewSlide(opt,container);
													}
												},
										swipeLeft:function()
												{

													if (opt.transition==0) {
															opt.next = opt.next+1;
															if (opt.next == opt.slideamount) opt.next=0;
															callingNewSlide(opt,container);
													}
												},
									allowPageScroll:"auto"} );
		}




		////////////////////////////////////////////////////////////////
		// SHOW AND HIDE THE THUMBS IF MOUE GOES OUT OF THE BANNER  ///
		//////////////////////////////////////////////////////////////
		function hideThumbs(container,opt) {

			var bullets = container.parent().find('.tp-bullets');
			var ca = container.parent().find('.tparrows');

			if (bullets==null) {
				container.append('<div class=".tp-bullets"></div>');
				var bullets = container.parent().find('.tp-bullets');
			}

			if (ca==null) {
				container.append('<div class=".tparrows"></div>');
				var ca = container.parent().find('.tparrows');
			}


			//var bp = (thumbs.parent().outerHeight(true) - opt.height)/2;

			//	ADD THUMBNAIL IMAGES FOR THE BULLETS //
			container.data('hidethumbs',opt.hideThumbs);



			try{ bullets.css({'opacity':0}); } catch(e) {}
			try { ca.css({'opacity':0}); } catch(e) {}

			bullets.hover(function() {
				bullets.addClass("hovered");
				clearTimeout(container.data('hidethumbs'));
				bullets.cssAnimate({'opacity':1},{duration:200,queue:false});
				ca.animate({'opacity':1},{duration:200,queue:false});
			},
			function() {

				bullets.removeClass("hovered");
				if (!container.hasClass("hovered") && !bullets.hasClass("hovered"))
					container.data('hidethumbs', setTimeout(function() {
						bullets.cssAnimate({'opacity':0},{duration:200,queue:false});
						ca.animate({'opacity':0},{duration:200,queue:false});
					},opt.hideThumbs));
			});


			ca.hover(function() {
				bullets.addClass("hovered");
				clearTimeout(container.data('hidethumbs'));
				bullets.cssAnimate({'opacity':1},{duration:200,queue:false});
				ca.animate({'opacity':1},{duration:200,queue:false});
			},
			function() {

				bullets.removeClass("hovered");
				if (!container.hasClass("hovered") && !bullets.hasClass("hovered"))
					container.data('hidethumbs', setTimeout(function() {
						bullets.cssAnimate({'opacity':0},{duration:200,queue:false});
						ca.animate({'opacity':0},{duration:200,queue:false});
					},opt.hideThumbs));
			});



			container.live('mouseenter', function() {
				container.addClass("hovered");
				clearTimeout(container.data('hidethumbs'));
				bullets.cssAnimate({'opacity':1},{duration:200,queue:false});
				ca.animate({'opacity':1},{duration:200,queue:false});
			});

			container.live('mouseleave', function() {
				container.removeClass("hovered");
				if (!container.hasClass("hovered") && !bullets.hasClass("hovered"))
					container.data('hidethumbs', setTimeout(function() {
								bullets.cssAnimate({'opacity':0},{duration:200,queue:false});
								ca.animate({'opacity':0},{duration:200,queue:false});
					},opt.hideThumbs));
			});

		}







		//////////////////////////////
		//	SET POSITION OF BULLETS	//
		//////////////////////////////
		function setBulPos(container,opt) {

			/* FOR THE PREVIEW WE NEED TO HANDLE IF BOTH NAVIGATION IS LOADED */
			if (opt.navigationType=="both") {
					opt.navigationType="bullet";
					opt.navsecond = "both";
			}
			if (opt.navigationType=="none" && opt.navigationArrows!="none") opt.navigationArrows="verticalcentered";



				opt.navOH = opt.navOffsetHorizontal * opt.bw;
				opt.navOV = opt.navOffsetVertical * opt.bh;
				if (opt.bw!=1) opt.navOH=0;

				// SOME HELP
				var cap=container.parent();
				var la=cap.find('.tp-leftarrow');
				var ra=cap.find('.tp-rightarrow');

				//////////////////////////////////////
				//	THE BULLET NAVIGATION POSITIONS //
				/////////////////////////////////////

				if (opt.navigationType=="bullet") {

							var bullets = cap.find('.tp-bullets.simplebullets');
							bullets.css({'visibility':'visible'});
							try{ cap.find('.tp-thumbs').css({'visibility':'hidden'});} catch(e) {}

							var fulllong=bullets.width();
							if (!bullets.hasClass("tp-thumbs")) {
								fulllong=0;
								bullets.find('.bullet').each(function() { fulllong = fulllong + $(this).outerWidth(true);});
								bullets.css({'width':(fulllong)+"px"});
							}

							var ldiff = cap.outerWidth()- opt.width;

							bullets.css({'left':(opt.navOH) + (ldiff/2)+(opt.width/2 - fulllong/2)+"px", 'bottom':opt.navOV+"px"});

							if (opt.navigationArrows=="nexttobullets") {

								la.removeClass("large");
								ra.removeClass("large");
								la.removeClass("thumbswitharrow");
								ra.removeClass("thumbswitharrow");
								la.css({'visibility':'visible'});
								ra.css({'visibility':'visible'});
								var diff = 0;

								la.css({'position':'absolute','left': (bullets.position().left - la.outerWidth(true))+"px",
															  'top':  bullets.position().top+"px"});

								ra.css({'position':'absolute','left': (bullets.outerWidth(true) + bullets.position().left)+"px",
															  'top':bullets.position().top+"px"});
							} else {

								if (opt.navigationArrows=="verticalcentered") {

									la.addClass("large");
									ra.addClass("large");
									la.css({'visibility':'visible'});
									ra.css({'visibility':'visible'});
									var decorh=cap.outerHeight();
									la.css({'position':'absolute','left': (ldiff/2)+"px",'top': (decorh/2)+"px"});
									ra.css({'position':'absolute','left': (opt.width - ra.outerWidth()+ldiff/2)+"px",'top': (decorh/2)+"px"});
								} else {

									la.css({'visibility':'hidden'});
									ra.css({'visibility':'hidden'});
								}
						}
					} else {

							//////////////////////////////////////
							//	THE THUMBS NAVIGATION POSITIONS //
							/////////////////////////////////////
							if (opt.navigationType=="thumb") {


								var thumbs=cap.find('.tp-thumbs');
								try{ cap.find('.tp-bullets').css({'visibility':'hidden'}); } catch(e) {}
								thumbs.css({'visibility':'visible'});



								var decorh=thumbs.parent().outerHeight();

								var ldiff = cap.outerWidth()- opt.width;

								thumbs.css({'left':(opt.navOH) + (opt.width/2 - thumbs.width()/2)+"px"});
								thumbs.css({'bottom':(0-thumbs.outerHeight(true)  + (opt.navOV))+"px"});

									if (opt.navigationArrows=="verticalcentered") {

										la.css({'visibility':'visible'});
										ra.css({'visibility':'visible'});
										la.addClass("large");
										ra.addClass("large");
										la.css({'position':'absolute','left': (ldiff/2)+"px",'top': (cap.outerHeight()/2 )+"px"});
										ra.css({'position':'absolute','left': (opt.width - ra.outerWidth()+ldiff/2)+"px",'top': (cap.outerHeight()/2)+"px"});
									} else {

										la.css({'visibility':'hidden'});
										ra.css({'visibility':'hidden'});
									}

							} else {
								if (opt.navigationType=="none") {

									try{ cap.find('.tp-bullets').css({'visibility':'hidden'}); } catch(e) {}
									try{ cap.find('.tp-thumbs').css({'visibility':'hidden'});} catch(e) {}

									if (opt.navigationArrows!="none") {
										var ldiff = cap.outerWidth()- opt.width;

										la.css({'visibility':'visible'});
										ra.css({'visibility':'visible'});
										la.addClass("large");
										ra.addClass("large");
										la.css({'position':'absolute','left': (ldiff/2)+"px",'top': (cap.outerHeight()/2)+"px"});
										ra.css({'position':'absolute','left': (opt.width - ra.outerWidth()+ldiff/2)+"px",'top': (cap.outerHeight()/2)+"px"});
									} else {

										la.css({'visibility':'hidden'});
										ra.css({'visibility':'hidden'});
									}
								}
							}
						}

		}



		//////////////////////////////////////////////////////////
		//	-	SET THE IMAGE SIZE TO FIT INTO THE CONTIANER -  //
		////////////////////////////////////////////////////////
		function setSize(img,opt) {


			opt.width=parseInt(opt.container.width(),0);
			opt.height=parseInt(opt.container.height(),0);

			opt.bw = opt.width / opt.startwidth;
			opt.bh = opt.height / opt.startheight;

			if (opt.bh>1) {
							opt.bw=1;
							opt.bh=1;
						}


			// IF IMG IS ALREADY PREPARED, WE RESET THE SIZE FIRST HERE
			if (img.data('orgw')!=undefined) {
				img.width(img.data('orgw'));
				img.height(img.data('orgh'));
			}


			var fw = opt.width / img.width();
			var fh = opt.height / img.height();


			opt.fw = fw;
			opt.fh = fh;

			if (img.data('orgw')==undefined) {
				img.data('orgw',img.width());
				img.data('orgh',img.height());
			}



			if (opt.fullWidth=="on") {

					var cow = opt.container.parent().width();
					var coh = opt.container.parent().height();
					var ffh = coh / img.data('orgh');
					var ffw = cow / img.data('orgw');


					img.width(img.width()*ffh);
					img.height(coh);

					if (img.width()<cow) {
						img.width(cow+50);
						var ffw = img.width() / img.data('orgw');
						img.height(img.data('orgh')*ffw);
					}

					if (img.width()>cow) {
						img.data("fxof",(cow/2 - img.width()/2));

						img.css({'position':'absolute','left':img.data('fxof')+"px"});
					}


			} else {

					img.width(opt.width);
					img.height(img.height()*fw);

					if (img.height()<opt.height && img.height()!=0 && img.height()!=null) {

						img.height(opt.height);
						img.width(img.data('orgw')*fh);
					}
			}



			img.data('neww',img.width());
			img.data('newh',img.height());
			if (opt.fullWidth=="on") {
				opt.slotw=Math.ceil(img.width()/opt.slots);
			} else {
				opt.slotw=Math.ceil(opt.width/opt.slots);
			}
			opt.sloth=Math.ceil(opt.height/opt.slots);

		}




		/////////////////////////////////////////
		//	-	PREPARE THE SLIDES / SLOTS -  //
		///////////////////////////////////////
		function prepareSlides(container,opt) {

			container.find('.caption').each(function() { $(this).addClass($(this).data('transition')); $(this).addClass('start') });

			container.find('ul:first >li').each(function(j) {
				var li=$(this);
				if (li.data('link')!=undefined) {
					var link = li.data('link');
					li.append('<div class="caption sft slidelink" data-x="0" data-y="0" data-start="0"><a href="'+link+'"><div></div></a></div>');

				}
			});

			container.find('ul:first li >img').each(function(j) {

				var img=$(this);
				img.addClass('defaultimg');
				setSize(img,opt);
				img.wrap('<div class="slotholder"></div>');
				img.css({'opacity':0});
				img.data('li-id',j);

			});
		}


		///////////////////////
		// PREPARE THE SLIDE //
		//////////////////////
		function prepareOneSlide(slotholder,opt,visible) {

				var sh=slotholder;
				var img = sh.find('img')
				setSize(img,opt)
				var src = img.attr('src');
				var w = img.data('neww');
				var h = img.data('newh');
				var fulloff = img.data("fxof");
				if (fulloff==undefined) fulloff=0;


				var off=0;


				if (!visible)
					var off=0-opt.slotw;

				for (var i=0;i<opt.slots;i++)
					sh.append('<div class="slot" style="position:absolute;top:0px;left:'+(fulloff+i*opt.slotw)+'px;overflow:hidden;width:'+opt.slotw+'px;height:'+h+'px"><div class="slotslide" style="position:absolute;top:0px;left:'+off+'px;width:'+opt.slotw+'px;height:'+h+'px;overflow:hidden;"><img style="position:absolute;top:0px;left:'+(0-(i*opt.slotw))+'px;width:'+w+'px;height:'+h+'px" src="'+src+'"></div></div>');

		}


		///////////////////////
		// PREPARE THE SLIDE //
		//////////////////////
		function prepareOneSlideV(slotholder,opt,visible) {

				var sh=slotholder;
				var img = sh.find('img')
				setSize(img,opt)
				var src = img.attr('src');
				var w = img.data('neww');
				var h = img.data('newh');
				var fulloff = img.data("fxof");
				if (fulloff==undefined) fulloff=0;
				var off=0;


				if (!visible)
					var off=0-opt.sloth;

				for (var i=0;i<opt.slots;i++)
					sh.append('<div class="slot" style="position:absolute;top:'+(i*opt.sloth)+'px;left:'+(fulloff)+'px;overflow:hidden;width:'+w+'px;height:'+(opt.sloth)+'px"><div class="slotslide" style="position:absolute;top:'+off+'px;left:0px;width:'+w+'px;height:'+opt.sloth+'px;overflow:hidden;"><img style="position:absolute;top:'+(0-(i*opt.sloth))+'px;left:0px;width:'+w+'px;height:'+h+'px" src="'+src+'"></div></div>');

		}


		///////////////////////
		// PREPARE THE SLIDE //
		//////////////////////
		function prepareOneSlideBox(slotholder,opt,visible) {

				var sh=slotholder;
				var img = sh.find('img')
				setSize(img,opt)
				var src = img.attr('src');
				var w = img.data('neww');
				var h = img.data('newh');
				var fulloff = img.data("fxof");
				if (fulloff==undefined) fulloff=0;
				var off=0;




				// SET THE MINIMAL SIZE OF A BOX
				var basicsize = 0;
				if (opt.sloth>opt.slotw)
					basicsize=opt.sloth
				else
					basicsize=opt.slotw;


				if (!visible) {
					var off=0-basicsize;
				}

				opt.slotw = basicsize;
				opt.sloth = basicsize;
				var x=0;
				var y=0;



				for (var j=0;j<opt.slots;j++) {

					y=0;
					for (var i=0;i<opt.slots;i++) 	{


						sh.append('<div class="slot" '+
								  'style="position:absolute;'+
											'top:'+y+'px;'+
											'left:'+(fulloff+x)+'px;'+
											'width:'+basicsize+'px;'+
											'height:'+basicsize+'px;'+
											'overflow:hidden;">'+

								  '<div class="slotslide" data-x="'+x+'" data-y="'+y+'" '+
								  'style="position:absolute;'+
											'top:'+(0)+'px;'+
											'left:'+(0)+'px;'+
											'width:'+basicsize+'px;'+
											'height:'+basicsize+'px;'+
											'overflow:hidden;">'+

								  '<img style="position:absolute;'+
											'top:'+(0-y)+'px;'+
											'left:'+(0-x)+'px;'+
											'width:'+w+'px;'+
											'height:'+h+'px"'+
								  'src="'+src+'"></div></div>');
						y=y+basicsize;
					}
					x=x+basicsize;
				}
		}





		///////////////////////
		//	REMOVE SLOTS	//
		/////////////////////
		function removeSlots(container) {

			container.find('.slotholder .slot').each(function() {
				clearTimeout($(this).data('tout'));
				$(this).remove();
			});

		}


		////////////////////////
		//	CAPTION POSITION  //
		///////////////////////
		function setCaptionPositions(container,opt) {

			// FIND THE RIGHT CAPTIONS
			var actli = container.find('li:eq('+opt.act+')');
			var nextli = container.find('li:eq('+opt.next+')');

			// SET THE NEXT CAPTION AND REMOVE THE LAST CAPTION
			var nextcaption=nextli.find('.caption');

			if (nextcaption.find('iframe')==0) {

				// MOVE THE CAPTIONS TO THE RIGHT POSITION
				if (nextcaption.hasClass('hcenter'))
					nextcaption.css({'height':opt.height+"px",'top':'0px','left':(opt.width/2 - nextcaption.outerWidth()/2)+'px'});
				else
					if (nextcaption.hasClass('vcenter'))
						nextcaption.css({'width':opt.width+"px",'left':'0px','top':(opt.height/2 - nextcaption.outerHeight()/2)+'px'});
			}
		}


		//////////////////////////////
		//                         //
		//	-	SWAP THE SLIDES -  //
		//                        //
		////////////////////////////
		function swapSlide(container,opt) {


			opt.transition = 1;
			opt.videoplaying = false;

			try{
				var actli = container.find('li:eq('+opt.act+')');
			} catch(e) {
				var actli=container.find('li:eq(1)');
			}


			var nextli = container.find('li:eq('+opt.next+')');

			var actsh = actli.find('.slotholder');
			var nextsh = nextli.find('.slotholder');
			actli.css({'visibility':'visible'});
			nextli.css({'visibility':'visible'});

			if ($.browser.msie && $.browser.version<9) {
				if (nextli.data('transition')=="boxfade") nextli.data('transition',"boxslide");
				if (nextli.data('transition')=="slotfade-vertical") nextli.data('transition',"slotzoom-vertical");
				if (nextli.data('transition')=="slotfade-horizontal") nextli.data('transition',"slotzoom-horizontal");
			}


			// IF DELAY HAS BEEN SET VIA THE SLIDE, WE TAKE THE NEW VALUE, OTHER WAY THE OLD ONE...
			if (nextli.data('delay')!=undefined) {
						opt.cd=0;
						opt.delay=nextli.data('delay');
			} else {
				opt.delay=opt.origcd;
			}

			// RESET POSITION AND FADES OF LI'S
			actli.css({'left':'0px','top':'0px'});
			nextli.css({'left':'0px','top':'0px'});

			///////////////////////////////////////
			// TRANSITION CHOOSE - RANDOM EFFECTS//
			///////////////////////////////////////
			var nexttrans = 0;




			if (nextli.data('transition')=="boxslide") nexttrans = 0
			  else
				if (nextli.data('transition')=="boxfade") nexttrans = 1
				  else
					if (nextli.data('transition')=="slotslide-horizontal") nexttrans = 2
					  else
						if (nextli.data('transition')=="slotslide-vertical") nexttrans = 3
						  else
						    if (nextli.data('transition')=="curtain-1") nexttrans = 4
							  else
								if (nextli.data('transition')=="curtain-2") nexttrans = 5
								 else
								   if (nextli.data('transition')=="curtain-3") nexttrans = 6
									 else
									   if (nextli.data('transition')=="slotzoom-horizontal") nexttrans = 7
									     else
											if (nextli.data('transition')=="slotzoom-vertical")  nexttrans = 8
											  else
												 if (nextli.data('transition')=="slotfade-horizontal")  nexttrans = 9
												    else
													   if (nextli.data('transition')=="slotfade-vertical") nexttrans = 10
													      else
															if (nextli.data('transition')=="fade") nexttrans = 11
															 else
																if (nextli.data('transition')=="slideleft")  nexttrans = 12
																	else
																		if (nextli.data('transition')=="slideup") nexttrans = 13
																			else
																				if (nextli.data('transition')=="slidedown") nexttrans = 14
																					else
																						if (nextli.data('transition')=="slideright") nexttrans = 15;
																							else {
																								nexttrans=Math.round(Math.random()*16);
																								nextli.data('slotamount',Math.round(Math.random()*12+4));
																							}

			if (nextli.data('transition')=="slidehorizontal") {
					if (opt.act<opt.next)
						nexttrans = 12
					else
						nexttrans = 15
				}

			if (nextli.data('transition')=="slidevertical") {
					if (opt.act<opt.next)
						nexttrans = 13
					else
						nexttrans = 14
				}


			if (nexttrans>16) nexttrans = 15;
			if (nexttrans<0) nexttrans = 0;

			// DEFINE THE MASTERSPEED FOR THE SLIDE //
			var masterspeed=300;
			if (nextli.data('masterspeed')!=undefined && nextli.data('masterspeed')>99 && nextli.data('masterspeed')<2001)
				masterspeed = nextli.data('masterspeed');



			/////////////////////////////////////////////
			// SET THE BULLETS SELECTED OR UNSELECTED  //
			/////////////////////////////////////////////


			container.parent().find(".bullet").each(function() {
				var bul = $(this);
				bul.removeClass("selected");
				if (bul.index() == opt.next) bul.addClass('selected');
			});


			//////////////////////////////////////////////////////////////////
			// 		SET THE NEXT CAPTION AND REMOVE THE LAST CAPTION		//
			//////////////////////////////////////////////////////////////////

					container.find('li').each(function() {
						var li = $(this);
						if (li.index!=opt.act && li.index!=opt.next) li.css({'z-index':16});
					});

					actli.css({'z-index':18});
					nextli.css({'z-index':20});
					nextli.css({'opacity':0});


			///////////////////////////
			//	ANIMATE THE CAPTIONS //
			///////////////////////////
			removeTheCaptions(actli,opt);
			animateTheCaptions(nextli, opt);




			/////////////////////////////////////////////
			//	SET THE ACTUAL AMOUNT OF SLIDES !!     //
			//  SET A RANDOM AMOUNT OF SLOTS          //
			///////////////////////////////////////////
						if (nextli.data('slotamount')==undefined || nextli.data('slotamount')<1) {
							opt.slots=Math.round(Math.random()*12+4);
							if (nextli.data('transition')=="boxslide")
								opt.slots=Math.round(Math.random()*6+3);
						 } else {
							opt.slots=nextli.data('slotamount');
						}




			/////////////////////////////////////
			// THE SLOTSLIDE - TRANSITION I.  //
			////////////////////////////////////
			if (nexttrans==0) {



						masterspeed = masterspeed + 100;


						if (opt.slots>15) opt.slots=15;

						nextli.css({'opacity':1});

						// PREPARE THE SLOTS HERE
						prepareOneSlideBox(actsh,opt,true);
						prepareOneSlideBox(nextsh,opt,false);

						//SET DEFAULT IMG UNVISIBLE
						nextsh.find('.defaultimg').css({'opacity':0});
						//actsh.find('.defaultimg').css({'opacity':0});


						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT

						nextsh.find('.slotslide').each(function(j) {
							var ss=$(this);
							ss.css({'top':(0-opt.sloth)+"px",'left':(0-opt.slotw)+"px"});


							setTimeout(function() {

									if (opt.firefox13)
											ss.animate({'top':"0px",'left':'0px'},{duration:(masterspeed),queue:false,complete:function() {
																	if (j==(opt.slots*opt.slots)-1) {
																		removeSlots(container);
																		nextsh.find('.defaultimg').css({'opacity':1});
																		actsh.find('.defaultimg').css({'opacity':0});
																		opt.act=opt.next;
																		opt.transition = 0;
																		moveSelectedThumb(container);
																	}

											}});

									else

											ss.cssAnimate({'top':"0px",'left':'0px'},{duration:(masterspeed),queue:false,complete:function() {
																	if (j==(opt.slots*opt.slots)-1) {
																		removeSlots(container);
																		nextsh.find('.defaultimg').css({'opacity':1});
																		actsh.find('.defaultimg').css({'opacity':0});
																		if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});

																		opt.act=opt.next;
																		opt.transition = 0;
																		moveSelectedThumb(container);
																	}

											}});
							},j*15);
						});
			}



			/////////////////////////////////////
			// THE SLOTSLIDE - TRANSITION I.  //
			////////////////////////////////////
			if (nexttrans==1) {


						if (opt.slots>15) opt.slots=15;
						nextli.css({'opacity':1});

						// PREPARE THE SLOTS HERE
						//prepareOneSlideBox(actsh,opt,true);
						prepareOneSlideBox(nextsh,opt,false);

						//SET DEFAULT IMG UNVISIBLE
						nextsh.find('.defaultimg').css({'opacity':0});
						//actsh.find('.defaultimg').css({'opacity':0});


						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT

						nextsh.find('.slotslide').each(function(j) {
							var ss=$(this);
							ss.css({'opacity':0});
							ss.find('img').css({'opacity':0});
							ss.find('img').css({'top':(Math.random()*opt.slotw-opt.slotw)+"px",'left':(Math.random()*opt.slotw-opt.slotw)+"px"});


							var rand=Math.random()*1000+(masterspeed + 200);
							if (j==(opt.slots*opt.slots)-1) rand=1500;
							if (opt.firefox13) {
									ss.find('img').animate({'opacity':1,'top':(0-ss.data('y'))+"px",'left':(0-ss.data('x'))+'px'},{duration:rand,queue:false});
									ss.animate({'opacity':1},{duration:rand,queue:false,complete:function() {
															if (j==(opt.slots*opt.slots)-1) {
																removeSlots(container);
																nextsh.find('.defaultimg').css({'opacity':1});
																actsh.find('.defaultimg').css({'opacity':0});
																opt.act=opt.next;
																opt.transition = 0;
																		moveSelectedThumb(container);
															}

									}});
							} else {
									ss.find('img').animate({'opacity':1,'top':(0-ss.data('y'))+"px",'left':(0-ss.data('x'))+'px'},{duration:rand,queue:false});
									ss.cssAnimate({'opacity':1},{duration:rand,queue:false,complete:function() {
															if (j==(opt.slots*opt.slots)-1) {
																removeSlots(container);
																nextsh.find('.defaultimg').css({'opacity':1});
																actsh.find('.defaultimg').css({'opacity':0});
																if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
																opt.act=opt.next;
																opt.transition = 0;
																		moveSelectedThumb(container);
															}

									}});
							}

						});
			}


			/////////////////////////////////////
			// THE SLOTSLIDE - TRANSITION I.  //
			////////////////////////////////////
			if (nexttrans==2) {


						masterspeed = masterspeed + 200;

						nextli.css({'opacity':1});

						// PREPARE THE SLOTS HERE
						prepareOneSlide(actsh,opt,true);
						prepareOneSlide(nextsh,opt,false);

						//SET DEFAULT IMG UNVISIBLE
						nextsh.find('.defaultimg').css({'opacity':0});
						//actsh.find('.defaultimg').css({'opacity':0});

						// ALL OLD SLOTS SHOULD BE SLIDED TO THE RIGHT
						actsh.find('.slotslide').each(function() {
							var ss=$(this);
							if (opt.firefox13) {

									ss.animate({'left':opt.slotw+'px'},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															opt.act=opt.next;
															opt.transition = 0;
																		moveSelectedThumb(container);

									}});
								} else {

									ss.cssAnimate({'left':opt.slotw+'px'},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															opt.act=opt.next;
															opt.transition = 0;
																		moveSelectedThumb(container);

									}});
								}
						});

						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT
						nextsh.find('.slotslide').each(function() {
							var ss=$(this);
							ss.css({'left':(0-opt.slotw)+"px"});
							if (opt.firefox13) {

									ss.animate({'left':'0px'},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
															opt.act=opt.next;
															opt.transition = 0;
																		moveSelectedThumb(container);

									}});
							} else {
									ss.cssAnimate({'left':'0px'},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															opt.act=opt.next;
															opt.transition = 0;
																		moveSelectedThumb(container);

									}});
							}
						});
			}



			/////////////////////////////////////
			// THE SLOTSLIDE - TRANSITION I.  //
			////////////////////////////////////
			if (nexttrans==3) {


						masterspeed = masterspeed + 200;
						nextli.css({'opacity':1});

						// PREPARE THE SLOTS HERE
						prepareOneSlideV(actsh,opt,true);
						prepareOneSlideV(nextsh,opt,false);

						//SET DEFAULT IMG UNVISIBLE
						nextsh.find('.defaultimg').css({'opacity':0});
						//actsh.find('.defaultimg').css({'opacity':0});

						// ALL OLD SLOTS SHOULD BE SLIDED TO THE RIGHT
						actsh.find('.slotslide').each(function() {
							var ss=$(this);
							if (opt.firefox13) {
									ss.animate({'top':opt.sloth+'px'},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															opt.act=opt.next;
															opt.transition = 0;
																		moveSelectedThumb(container);

									}});
							} else {
									ss.cssAnimate({'top':opt.sloth+'px'},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
															opt.act=opt.next;
															opt.transition = 0;
																		moveSelectedThumb(container);

									}});
							}
						});

						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT
						nextsh.find('.slotslide').each(function() {
							var ss=$(this);
							ss.css({'top':(0-opt.sloth)+"px"});
							if (opt.firefox13) {
								ss.animate({'top':'0px'},{duration:masterspeed,queue:false,complete:function() {
													removeSlots(container);
													nextsh.find('.defaultimg').css({'opacity':1});
													actsh.find('.defaultimg').css({'opacity':0});
													opt.act=opt.next;
													opt.transition = 0;
																moveSelectedThumb(container);

								}});
							} else {
								ss.cssAnimate({'top':'0px'},{duration:masterspeed,queue:false,complete:function() {
													removeSlots(container);
													nextsh.find('.defaultimg').css({'opacity':1});
													actsh.find('.defaultimg').css({'opacity':0});
													if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
													opt.act=opt.next;
													opt.transition = 0;
																moveSelectedThumb(container);

								}});
							}
						});
			}



			/////////////////////////////////////
			// THE SLOTSLIDE - TRANSITION I.  //
			////////////////////////////////////
			if (nexttrans==4) {



						nextli.css({'opacity':1});

						// PREPARE THE SLOTS HERE
						prepareOneSlide(actsh,opt,true);
						prepareOneSlide(nextsh,opt,true);

						//SET DEFAULT IMG UNVISIBLE
						nextsh.find('.defaultimg').css({'opacity':0});
						actsh.find('.defaultimg').css({'opacity':0});


						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT
						actsh.find('.slotslide').each(function(i) {
							var ss=$(this);

							ss.cssAnimate({'top':(0+(opt.height))+"px",'opacity':1},{duration:masterspeed+(i*(70-opt.slots)),queue:false,complete:function() {


							}});
						});

						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT
						nextsh.find('.slotslide').each(function(i) {
							var ss=$(this);
							ss.css({'top':(0-(opt.height))+"px",'opacity':0});
							if (opt.firefox13) {
									ss.animate({'top':'0px','opacity':1},{duration:masterspeed+(i*(70-opt.slots)),queue:false,complete:function() {
															if (i==opt.slots-1) {
																removeSlots(container);
																nextsh.find('.defaultimg').css({'opacity':1});
																actsh.find('.defaultimg').css({'opacity':0});
																opt.act=opt.next;
																opt.transition = 0;
																		moveSelectedThumb(container);
															}

									}});
							} else {
									ss.cssAnimate({'top':'0px','opacity':1},{duration:masterspeed+(i*(70-opt.slots)),queue:false,complete:function() {
															if (i==opt.slots-1) {
																removeSlots(container);
																nextsh.find('.defaultimg').css({'opacity':1});
																actsh.find('.defaultimg').css({'opacity':0});
																if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
																opt.act=opt.next;
																opt.transition = 0;
																		moveSelectedThumb(container);
															}

									}});
							}
						});
			}


			/////////////////////////////////////
			// THE SLOTSLIDE - TRANSITION I.  //
			////////////////////////////////////
			if (nexttrans==5) {



						nextli.css({'opacity':1});

						// PREPARE THE SLOTS HERE
						prepareOneSlide(actsh,opt,true);
						prepareOneSlide(nextsh,opt,true);

						//SET DEFAULT IMG UNVISIBLE
						nextsh.find('.defaultimg').css({'opacity':0});
						actsh.find('.defaultimg').css({'opacity':0});

						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT
						actsh.find('.slotslide').each(function(i) {
							var ss=$(this);
							if (opt.firefox13) {
									ss.animate({'top':(0+(opt.height))+"px",'opacity':1},{duration:masterspeed+((opt.slots-i)*(70-opt.slots)),queue:false,complete:function() {
									}});
							} else {
									ss.cssAnimate({'top':(0+(opt.height))+"px",'opacity':1},{duration:masterspeed+((opt.slots-i)*(70-opt.slots)),queue:false,complete:function() {
									}});
							}
						});

						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT
						nextsh.find('.slotslide').each(function(i) {
							var ss=$(this);
							ss.css({'top':(0-(opt.height))+"px",'opacity':0});
							if (opt.firefox13) {
									ss.animate({'top':'0px','opacity':1},{duration:masterspeed+((opt.slots-i)*(70-opt.slots)),queue:false,complete:function() {
															if (i==0) {
																removeSlots(container);
																nextsh.find('.defaultimg').css({'opacity':1});
																actsh.find('.defaultimg').css({'opacity':0});
																opt.act=opt.next;
																opt.transition = 0;
																																moveSelectedThumb(container);
															}

									}});
							} else {
										ss.cssAnimate({'top':'0px','opacity':1},{duration:masterspeed+((opt.slots-i)*(70-opt.slots)),queue:false,complete:function() {
															if (i==0) {
																removeSlots(container);
																nextsh.find('.defaultimg').css({'opacity':1});
																actsh.find('.defaultimg').css({'opacity':0});
																if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
																opt.act=opt.next;
																opt.transition = 0;
																																moveSelectedThumb(container);
															}

									}});
							}
						});
			}


			/////////////////////////////////////
			// THE SLOTSLIDE - TRANSITION I.  //
			////////////////////////////////////
			if (nexttrans==6) {



						nextli.css({'opacity':1});
						if (opt.slots<2) opt.slots=2;
						// PREPARE THE SLOTS HERE
						prepareOneSlide(actsh,opt,true);
						prepareOneSlide(nextsh,opt,true);

						//SET DEFAULT IMG UNVISIBLE
						nextsh.find('.defaultimg').css({'opacity':0});
						actsh.find('.defaultimg').css({'opacity':0});


						actsh.find('.slotslide').each(function(i) {
							var ss=$(this);

							if (i<opt.slots/2)
								var tempo = (i+2)*60;
							else
								var tempo = (2+opt.slots-i)*60;

							if (opt.firefox13) {
									ss.animate({'top':(0+(opt.height))+"px",'opacity':1},{duration:masterspeed+tempo,queue:false,complete:function() {}});
							} else {
									ss.cssAnimate({'top':(0+(opt.height))+"px",'opacity':1},{duration:masterspeed+tempo,queue:false,complete:function() {}});
							}
						});

						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT
						nextsh.find('.slotslide').each(function(i) {
							var ss=$(this);
							ss.css({'top':(0-(opt.height))+"px",'opacity':0});
							if (i<opt.slots/2)
								var tempo = (i+2)*60;
							else
								var tempo = (2+opt.slots-i)*60;

							if (opt.firefox13) {
									ss.animate({'top':'0px','opacity':1},{duration:masterspeed+tempo,queue:false,complete:function() {
															if (i==Math.round(opt.slots/2)) {
																removeSlots(container);
																nextsh.find('.defaultimg').css({'opacity':1});
																actsh.find('.defaultimg').css({'opacity':0});
																opt.act=opt.next;
																opt.transition = 0;
																																moveSelectedThumb(container);
															}

									}});
							} else {
									ss.cssAnimate({'top':'0px','opacity':1},{duration:masterspeed+tempo,queue:false,complete:function() {
															if (i==Math.round(opt.slots/2)) {
																removeSlots(container);
																nextsh.find('.defaultimg').css({'opacity':1});
																actsh.find('.defaultimg').css({'opacity':0});
																if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
																opt.act=opt.next;
																opt.transition = 0;
																																moveSelectedThumb(container);
															}

									}});
							}
						});
			}


			////////////////////////////////////
			// THE SLOTSZOOM - TRANSITION II. //
			////////////////////////////////////
			if (nexttrans==7) {

						masterspeed = masterspeed * 3;
						nextli.css({'opacity':1});

						// PREPARE THE SLOTS HERE
						prepareOneSlide(actsh,opt,true);
						prepareOneSlide(nextsh,opt,true);

						//SET DEFAULT IMG UNVISIBLE
						nextsh.find('.defaultimg').css({'opacity':0});
						//actsh.find('.defaultimg').css({'opacity':0});

						// ALL OLD SLOTS SHOULD BE SLIDED TO THE RIGHT
						actsh.find('.slotslide').each(function() {
							var ss=$(this).find('img');
							if (opt.firefox13) {
									ss.animate({'left':(0-opt.slotw/2)+'px',
												   'top':(0-opt.height/2)+'px',
												   'width':(opt.slotw*2)+"px",
												   'height':(opt.height*2)+"px",
												   opacity:0
													},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															opt.transition = 0;
															opt.act = opt.next;
																															moveSelectedThumb(container);
													}});
							}	else	{

										ss.cssAnimate({'left':(0-opt.slotw/2)+'px',
												   'top':(0-opt.height/2)+'px',
												   'width':(opt.slotw*2)+"px",
												   'height':(opt.height*2)+"px",
												   opacity:0
													},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
															opt.transition = 0;
															opt.act = opt.next;
																															moveSelectedThumb(container);
													}});
							}
						});


						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT //
						///////////////////////////////////////////////////////////////
						nextsh.find('.slotslide').each(function(i) {
							var ss=$(this).find('img');
							ss.css({'left':(0)+'px',
									'top':(0)+'px',
									//'width':(opt.width*2)+"px",
									//'height':(opt.height*2)+"px",
									opacity:0});
							if (opt.firefox13) {
									ss.animate({'left':(0-i*opt.slotw)+'px',
												   'top':(0)+'px',
												   'width':(nextsh.find('.defaultimg').data('neww'))+"px",
												   'height':(nextsh.find('.defaultimg').data('newh'))+"px",
												   opacity:1
													},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															opt.transition = 0;
															opt.act = opt.next;
																															moveSelectedThumb(container);
													}});

							} else {
								 ss.cssAnimate({'left':(0-i*opt.slotw)+'px',
												   'top':(0)+'px',
												   'width':(nextsh.find('.defaultimg').data('neww'))+"px",
												   'height':(nextsh.find('.defaultimg').data('newh'))+"px",
												   opacity:1
													},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															opt.transition = 0;
															opt.act = opt.next;
																															moveSelectedThumb(container);
													}});

							}
						});
			}




			////////////////////////////////////
			// THE SLOTSZOOM - TRANSITION II. //
			////////////////////////////////////
			if (nexttrans==8) {

						masterspeed = masterspeed * 3;
						nextli.css({'opacity':1});

						// PREPARE THE SLOTS HERE
						prepareOneSlideV(actsh,opt,true);
						prepareOneSlideV(nextsh,opt,true);

						//SET DEFAULT IMG UNVISIBLE
						nextsh.find('.defaultimg').css({'opacity':0});
						//actsh.find('.defaultimg').css({'opacity':0});

						// ALL OLD SLOTS SHOULD BE SLIDED TO THE RIGHT
						actsh.find('.slotslide').each(function() {
							var ss=$(this).find('img');
							if (opt.firefox13) {
									ss.animate({'left':(0-opt.width/2)+'px',
												   'top':(0-opt.sloth/2)+'px',
												   'width':(opt.width*2)+"px",
												   'height':(opt.sloth*2)+"px",
												   opacity:0
													},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															opt.transition = 0;
															opt.act = opt.next;
															moveSelectedThumb(container);
													}});
							} else {

											ss.cssAnimate({'left':(0-opt.width/2)+'px',
												   'top':(0-opt.sloth/2)+'px',
												   'width':(opt.width*2)+"px",
												   'height':(opt.sloth*2)+"px",
												   opacity:0
													},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
															opt.transition = 0;
															opt.act = opt.next;
															moveSelectedThumb(container);
													}});
							}
						});


						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT //
						///////////////////////////////////////////////////////////////
						nextsh.find('.slotslide').each(function(i) {
							var ss=$(this).find('img');
							ss.css({'left':(0)+'px',
									'top':(0)+'px',
									//'width':(opt.width*2)+"px",
									//'height':(opt.height*2)+"px",
									opacity:0});
							if (opt.firefox13) {
									ss.animate({'left':(0)+'px',
												   'top':(0-i*opt.sloth)+'px',
												   'width':(nextsh.find('.defaultimg').data('neww'))+"px",
												   'height':(nextsh.find('.defaultimg').data('newh'))+"px",
												   opacity:1
													},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															opt.transition = 0;
															opt.act = opt.next;
															moveSelectedThumb(container);
													}});
							} else {
									ss.cssAnimate({'left':(0)+'px',
												   'top':(0-i*opt.sloth)+'px',
												   'width':(nextsh.find('.defaultimg').data('neww'))+"px",
												   'height':(nextsh.find('.defaultimg').data('newh'))+"px",
												   opacity:1
													},{duration:masterspeed,queue:false,complete:function() {
															removeSlots(container);
															nextsh.find('.defaultimg').css({'opacity':1});
															actsh.find('.defaultimg').css({'opacity':0});
															if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
															opt.transition = 0;
															opt.act = opt.next;
															moveSelectedThumb(container);
													}});

							}
						});
			}


			////////////////////////////////////////
			// THE SLOTSFADE - TRANSITION III.   //
			//////////////////////////////////////
			if (nexttrans==9) {



						nextli.css({'opacity':1});

						opt.slots = opt.width/20;

						prepareOneSlide(nextsh,opt,true);


						//actsh.find('.defaultimg').css({'opacity':0});
						nextsh.find('.defaultimg').css({'opacity':0});

						var ssamount=0;
						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT
						nextsh.find('.slotslide').each(function(i) {
							var ss=$(this);
							ssamount++;
							ss.css({'opacity':0});
							ss.data('tout',setTimeout(function() {
											ss.cssAnimate({'opacity':1},{duration:masterspeed,queue:false});

											},i*4)
									);

						});

						setTimeout(function() {
									removeSlots(container);
									nextsh.find('.defaultimg').css({'opacity':1});
									actsh.find('.defaultimg').css({'opacity':0});
									if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
									opt.transition = 0;
									opt.act = opt.next;
									moveSelectedThumb(container);
							},(masterspeed+(ssamount*4)));
			}




			////////////////////////////////////////
			// THE SLOTSFADE - TRANSITION III.   //
			//////////////////////////////////////
			if (nexttrans==10) {



						nextli.css({'opacity':1});

						opt.slots = opt.height/20;

						prepareOneSlideV(nextsh,opt,true);


						//actsh.find('.defaultimg').css({'opacity':0});
						nextsh.find('.defaultimg').css({'opacity':0});

						var ssamount=0;
						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT
						nextsh.find('.slotslide').each(function(i) {
							var ss=$(this);
							ssamount++;
							ss.css({'opacity':0});
							ss.data('tout',setTimeout(function() {
											ss.animate({'opacity':1},{duration:masterspeed,queue:false});

											},i*4)
									);

						});

						setTimeout(function() {
									removeSlots(container);
									nextsh.find('.defaultimg').css({'opacity':1});
									actsh.find('.defaultimg').css({'opacity':0});
									if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
									opt.transition = 0;
									opt.act = opt.next;
									moveSelectedThumb(container);
							},(masterspeed+(ssamount*4)));
			}


			///////////////////////////
			// SIMPLE FADE ANIMATION //
			///////////////////////////

			if (nexttrans==11) {



						nextli.css({'opacity':1});

						opt.slots = 1;

						prepareOneSlide(nextsh,opt,true);


						//actsh.find('.defaultimg').css({'opacity':0});
						nextsh.find('.defaultimg').css({'opacity':0});

						var ssamount=0;
						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT
						nextsh.find('.slotslide').each(function(i) {
							var ss=$(this);
							ssamount++;
							ss.css({'opacity':0});
							ss.animate({'opacity':1},{duration:masterspeed,queue:false});
						});

						setTimeout(function() {
									removeSlots(container);
									nextsh.find('.defaultimg').css({'opacity':1});
									actsh.find('.defaultimg').css({'opacity':0});
									if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
									opt.transition = 0;
									opt.act = opt.next;
									moveSelectedThumb(container);
							},masterspeed);
			}





			if (nexttrans==12 || nexttrans==13 || nexttrans==14 || nexttrans==15) {

						masterspeed = masterspeed * 3;
						nextli.css({'opacity':1});

						opt.slots = 1;

						prepareOneSlide(nextsh,opt,true);
						prepareOneSlide(actsh,opt,true);


						actsh.find('.defaultimg').css({'opacity':0});
						nextsh.find('.defaultimg').css({'opacity':0});

						var oow = opt.width;
						var ooh = opt.height;
						if (opt.fullWidth=="on") {
							oow=opt.container.parent().width();
							ooh=opt.container.parent().height();

						}

						// ALL NEW SLOTS SHOULD BE SLIDED FROM THE LEFT TO THE RIGHT
						var ssn=nextsh.find('.slotslide')
						if (nexttrans==12)
							ssn.css({'left':oow+"px"});
						else
							if (nexttrans==15)
								ssn.css({'left':(0-opt.width)+"px"});
							else
								if (nexttrans==13)
									ssn.css({'top':(ooh)+"px"});
								else
									if (nexttrans==14)
										ssn.css({'top':(0-opt.height)+"px"});

						if (opt.firefox13) {
										ssn.animate({'left':'0px','top':'0px',opacity:1},{duration:masterspeed,queue:false,complete:function() {
														removeSlots(container);
														nextsh.find('.defaultimg').css({'opacity':1});
														actsh.find('.defaultimg').css({'opacity':0});
														opt.transition = 0;
														opt.act = opt.next;
														moveSelectedThumb(container);
												}});
						} else {
										ssn.cssAnimate({'left':'0px','top':'0px',opacity:1},{duration:masterspeed,queue:false,complete:function() {
														removeSlots(container);
														nextsh.find('.defaultimg').css({'opacity':1});
														actsh.find('.defaultimg').css({'opacity':0});
														if ($.browser.msie && $.browser.version<9) actsh.find('.defaultimg').css({'opacity':1});
														opt.transition = 0;
														opt.act = opt.next;
														moveSelectedThumb(container);
												}});
						}


						var ssa=actsh.find('.slotslide');
						if (opt.firefox13) {
								if (nexttrans==12)
									ssa.animate({'left':(0-oow)+'px',opacity:1},{duration:masterspeed,queue:false});
								else
									if (nexttrans==15)
										ssa.animate({'left':(oow)+'px',opacity:1},{duration:masterspeed,queue:false});
									else
										if (nexttrans==13)
											ssa.animate({'top':(0-ooh)+'px',opacity:1},{duration:masterspeed,queue:false});
										else
											if (nexttrans==14)
												ssa.animate({'top':(ooh)+'px',opacity:1},{duration:masterspeed,queue:false});
						} else {
								if (nexttrans==12)
									ssa.cssAnimate({'left':(0-oow)+'px',opacity:1},{duration:masterspeed,queue:false});
								else
									if (nexttrans==15)
										ssa.cssAnimate({'left':(oow)+'px',opacity:1},{duration:masterspeed,queue:false});
									else
										if (nexttrans==13)
											ssa.cssAnimate({'top':(0-ooh)+'px',opacity:1},{duration:masterspeed,queue:false});
										else
											if (nexttrans==14)
												ssa.cssAnimate({'top':(ooh)+'px',opacity:1},{duration:masterspeed,queue:false});
						}




			}



		}

				//////////////////////////
				//	REMOVE THE CAPTIONS //
				/////////////////////////
				function removeTheCaptions(actli,opt) {
						actli.find('.caption').each(function(i) {
							var nextcaption=actli.find('.caption:eq('+i+')');
							nextcaption.stop(true,true);
							clearTimeout(nextcaption.data('timer'));
							var easetype=nextcaption.data('easing');
							easetype="easeInOutSine";
							var ll = nextcaption.data('repx');
							var tt = nextcaption.data('repy');
							var oo = nextcaption.data('repo');


							if (nextcaption.find('iframe').length>0) {
									var par=nextcaption.find('iframe').parent();
									var iframe=par.html();
								setTimeout(function() {
									nextcaption.find('iframe').remove();
									par.append(iframe);
								},nextcaption.data('speed'));
							}
							try {nextcaption.animate({'opacity':oo,'left':ll+'px','top':tt+"px"},{duration:nextcaption.data('speed'), easing:easetype});} catch(e) {}
						});
				}



				function onYouTubePlayerAPIReady() {

							}


				//////////////////////////////////////////
				// CHANG THE YOUTUBE PLAYER STATE HERE //
				////////////////////////////////////////
				 function onPlayerStateChange(event) {
					if (event.data == YT.PlayerState.PLAYING) {

						var bt = $('body').find('.tp-bannertimer');
						var opt = bt.data('opt');
						bt.stop();
						opt.videoplaying=true;

					} else {

						var bt = $('body').find('.tp-bannertimer');
						var opt = bt.data('opt');
						if (opt.conthover==0)
							bt.animate({'width':"100%"},{duration:((opt.delay-opt.cd)-100),queue:false, easing:"linear"});
						opt.videoplaying=false;
					}
				  }

				 ////////////////////////
				// VIMEO ADD EVENT /////
				////////////////////////
				function addEvent(element, eventName, callback) {

							if (element.addEventListener) {

								element.addEventListener(eventName, callback, false);
							}
							else {

								element.attachEvent(eventName, callback, false);
							}


						}

				//////////////////////////////////////////
				// CHANG THE YOUTUBE PLAYER STATE HERE //
				////////////////////////////////////////
				  function vimeoready(player_id) {

						var froogaloop = $f(player_id);

						froogaloop.addEvent('play', function(data) {
							var bt = $('body').find('.tp-bannertimer');
							var opt = bt.data('opt');
							bt.stop();
							opt.videoplaying=true;
						});

						froogaloop.addEvent('finish', function(data) {
								var bt = $('body').find('.tp-bannertimer');
								var opt = bt.data('opt');
								if (opt.conthover==0)
									bt.animate({'width':"100%"},{duration:((opt.delay-opt.cd)-100),queue:false, easing:"linear"});
								opt.videoplaying=false;
						});

						froogaloop.addEvent('pause', function(data) {
								var bt = $('body').find('.tp-bannertimer');
								var opt = bt.data('opt');
								if (opt.conthover==0)
									bt.animate({'width':"100%"},{duration:((opt.delay-opt.cd)-100),queue:false, easing:"linear"});
								opt.videoplaying=false;
						});


					}




				////////////////////////
				// SHOW THE CAPTION  //
				///////////////////////
				function animateTheCaptions(nextli, opt) {




						nextli.find('.caption').each(function(i) {

								offsetx = opt.width/2 - opt.startwidth/2;

								if (opt.bh>1) {
									opt.bw=1;
									opt.bh=1;
								}

								if (opt.bw>1) {
									opt.bw=1;
									opt.bh=1;
								}

								var xbw = opt.bw;




								var nextcaption=nextli.find('.caption:eq('+i+')');
								nextcaption.stop(true,true);


								if (nextcaption.hasClass("coloredbg")) offsetx=0;
								if (offsetx<0) offsetx=0;

								clearTimeout(nextcaption.data('timer'));



								// YOUTUBE AND VIMEO LISTENRES INITIALISATION

								var frameID = "iframe"+Math.round(Math.random()*1000+1);

								if (nextcaption.find('iframe').length>0) {
									var ifr = nextcaption.find('iframe');

									if (ifr.attr('src').toLowerCase().indexOf('youtube')>=0) {

												ifr.attr('id',frameID);
												ifr.addClass("HasListener");
												var player;
												player = new YT.Player(frameID, {
													events: {
														"onStateChange": onPlayerStateChange
													}
												});

									} else {
										if (ifr.attr('src').toLowerCase().indexOf('vimeo')>=0) {

											   if (!ifr.hasClass("HasListener")) {
													ifr.addClass("HasListener");
													ifr.attr('id',frameID);
													var isrc = ifr.attr('src');
													var queryParameters = {}, queryString = isrc,
													re = /([^&=]+)=([^&]*)/g, m;
													// Creates a map with the query string parameters
													while (m = re.exec(queryString)) {
														queryParameters[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
													}


													if (queryParameters['player_id']!=undefined) {

														isrc = isrc.replace(queryParameters['player_id'],frameID);
													} else {
														isrc=isrc+"&player_id="+frameID;
													}

													try{
															isrc = isrc.replace('api=0','api=1');
														} catch(e) {}

													isrc=isrc+"&api=1";



													ifr.attr('src',isrc);
													var player = nextcaption.find('iframe')[0];
													$f(player).addEvent('ready', vimeoready);

											   }

										}
									}
								}






							   var imw =0;
							   var imh = 0;

										if (nextcaption.find('img').length>0) {
											var im = nextcaption.find('img');
											if (im.data('ww') == undefined) im.data('ww',im.width());
											if (im.data('hh') == undefined) im.data('hh',im.height());

											var ww = im.data('ww');
											var hh = im.data('hh');


											im.width(ww*opt.bw);
											im.height(hh*opt.bh);
											imw = im.width();
											imh = im.height();
										} else {

											if (nextcaption.find('iframe').length>0) {
												var im = nextcaption.find('iframe');
												if (nextcaption.data('ww') == undefined) {
													nextcaption.data('ww',im.width());
												}
												if (nextcaption.data('hh') == undefined) nextcaption.data('hh',im.height());

												var ww = nextcaption.data('ww');
												var hh = nextcaption.data('hh');

												var nc =nextcaption;
													if (nc.data('fsize') == undefined) nc.data('fsize',parseInt(nc.css('font-size'),0) || 0);
													if (nc.data('pt') == undefined) nc.data('pt',parseInt(nc.css('paddingTop'),0) || 0);
													if (nc.data('pb') == undefined) nc.data('pb',parseInt(nc.css('paddingBottom'),0) || 0);
													if (nc.data('pl') == undefined) nc.data('pl',parseInt(nc.css('paddingLeft'),0) || 0);
													if (nc.data('pr') == undefined) nc.data('pr',parseInt(nc.css('paddingRight'),0) || 0);

													if (nc.data('mt') == undefined) nc.data('mt',parseInt(nc.css('marginTop'),0) || 0);
													if (nc.data('mb') == undefined) nc.data('mb',parseInt(nc.css('marginBottom'),0) || 0);
													if (nc.data('ml') == undefined) nc.data('ml',parseInt(nc.css('marginLeft'),0) || 0);
													if (nc.data('mr') == undefined) nc.data('mr',parseInt(nc.css('marginRight'),0) || 0);

													if (nc.data('bt') == undefined) nc.data('bt',parseInt(nc.css('borderTop'),0) || 0);
													if (nc.data('bb') == undefined) nc.data('bb',parseInt(nc.css('borderBottom'),0) || 0);
													if (nc.data('bl') == undefined) nc.data('bl',parseInt(nc.css('borderLeft'),0) || 0);
													if (nc.data('br') == undefined) nc.data('br',parseInt(nc.css('borderRight'),0) || 0);

													if (nc.data('lh') == undefined) nc.data('lh',parseInt(nc.css('lineHeight'),0) || 0);


													nextcaption.css({
																	 'font-size': (nc.data('fsize') * opt.bw)+"px",

																	 'padding-top': (nc.data('pt') * opt.bh) + "px",
																	 'padding-bottom': (nc.data('pb') * opt.bh) + "px",
																	 'padding-left': (nc.data('pl') * opt.bw) + "px",
																	 'padding-right': (nc.data('pr') * opt.bw) + "px",

																	 'margin-top': (nc.data('mt') * opt.bh) + "px",
																	 'margin-bottom': (nc.data('mb') * opt.bh) + "px",
																	 'margin-left': (nc.data('ml') * opt.bw) + "px",
																	 'margin-right': (nc.data('mr') * opt.bw) + "px",

																	 'border-top': (nc.data('bt') * opt.bh) + "px",
																	 'border-bottom': (nc.data('bb') * opt.bh) + "px",
																	 'border-left': (nc.data('bl') * opt.bw) + "px",
																	 'border-right': (nc.data('br') * opt.bw) + "px",

																	 'line-height': (nc.data('lh') * opt.bh) + "px",
																	 'height':(hh*opt.bh)+'px',
																	 'white-space':"nowrap"


													});

												im.width(ww*opt.bw);
												im.height(hh*opt.bh);
												imw = im.width();
												imh = im.height();
											} else {

													var nc =nextcaption;
													if (nc.data('fsize') == undefined) nc.data('fsize',parseInt(nc.css('font-size'),0) || 0);
													if (nc.data('pt') == undefined) nc.data('pt',parseInt(nc.css('paddingTop'),0) || 0);
													if (nc.data('pb') == undefined) nc.data('pb',parseInt(nc.css('paddingBottom'),0) || 0);
													if (nc.data('pl') == undefined) nc.data('pl',parseInt(nc.css('paddingLeft'),0) || 0);
													if (nc.data('pr') == undefined) nc.data('pr',parseInt(nc.css('paddingRight'),0) || 0);

													if (nc.data('mt') == undefined) nc.data('mt',parseInt(nc.css('marginTop'),0) || 0);
													if (nc.data('mb') == undefined) nc.data('mb',parseInt(nc.css('marginBottom'),0) || 0);
													if (nc.data('ml') == undefined) nc.data('ml',parseInt(nc.css('marginLeft'),0) || 0);
													if (nc.data('mr') == undefined) nc.data('mr',parseInt(nc.css('marginRight'),0) || 0);

													if (nc.data('bt') == undefined) nc.data('bt',parseInt(nc.css('borderTop'),0) || 0);
													if (nc.data('bb') == undefined) nc.data('bb',parseInt(nc.css('borderBottom'),0) || 0);
													if (nc.data('bl') == undefined) nc.data('bl',parseInt(nc.css('borderLeft'),0) || 0);
													if (nc.data('br') == undefined) nc.data('br',parseInt(nc.css('borderRight'),0) || 0);

													if (nc.data('lh') == undefined) nc.data('lh',parseInt(nc.css('lineHeight'),0) || 0);


													nextcaption.css({
																	 'font-size': (nc.data('fsize') * opt.bw)+"px",

																	 'padding-top': (nc.data('pt') * opt.bh) + "px",
																	 'padding-bottom': (nc.data('pb') * opt.bh) + "px",
																	 'padding-left': (nc.data('pl') * opt.bw) + "px",
																	 'padding-right': (nc.data('pr') * opt.bw) + "px",

																	 'margin-top': (nc.data('mt') * opt.bh) + "px",
																	 'margin-bottom': (nc.data('mb') * opt.bh) + "px",
																	 'margin-left': (nc.data('ml') * opt.bw) + "px",
																	 'margin-right': (nc.data('mr') * opt.bw) + "px",

																	 'border-top': (nc.data('bt') * opt.bh) + "px",
																	 'border-bottom': (nc.data('bb') * opt.bh) + "px",
																	 'border-left': (nc.data('bl') * opt.bw) + "px",
																	 'border-right': (nc.data('br') * opt.bw) + "px",

																	 'line-height': (nc.data('lh') * opt.bh) + "px",
																	 'white-space':"nowrap"


													});
													imh=nextcaption.outerHeight(true);
													imw=nextcaption.outerWidth(true);
												}
										}



								if (nextcaption.hasClass('fade')) {

									nextcaption.css({'opacity':0,'left':(xbw*nextcaption.data('x')+offsetx)+'px','top':(opt.bh*nextcaption.data('y'))+"px"});
								}



								if (nextcaption.hasClass('lfr')) {

									nextcaption.css({'opacity':1,'left':(5+opt.width)+'px','top':(opt.bh*nextcaption.data('y'))+"px"});

								}

								if (nextcaption.hasClass('lfl')) {

									nextcaption.css({'opacity':1,'left':(-5-imw)+'px','top':(opt.bh*nextcaption.data('y'))+"px"});

								}

								if (nextcaption.hasClass('sfl')) {

									nextcaption.css({'opacity':0,'left':((xbw*nextcaption.data('x'))-50+offsetx)+'px','top':(opt.bh*nextcaption.data('y'))+"px"});
								}

								if (nextcaption.hasClass('sfr')) {
									nextcaption.css({'opacity':0,'left':((xbw*nextcaption.data('x'))+50+offsetx)+'px','top':(opt.bh*nextcaption.data('y'))+"px"});
								}




								if (nextcaption.hasClass('lft')) {

									nextcaption.css({'opacity':1,'left':(xbw*nextcaption.data('x')+offsetx)+'px','top':(-5 - imh)+"px"});

								}

								if (nextcaption.hasClass('lfb')) {
									nextcaption.css({'opacity':1,'left':(xbw*nextcaption.data('x')+offsetx)+'px','top':(5+opt.height)+"px"});

								}

								if (nextcaption.hasClass('sft')) {
									nextcaption.css({'opacity':0,'left':(xbw*nextcaption.data('x')+offsetx)+'px','top':((opt.bh*nextcaption.data('y'))-50)+"px"});
								}

								if (nextcaption.hasClass('sfb')) {
									nextcaption.css({'opacity':0,'left':(xbw*nextcaption.data('x')+offsetx)+'px','top':((opt.bh*nextcaption.data('y'))+50)+"px"});
								}




								nextcaption.data('timer',setTimeout(function() {
										if (nextcaption.hasClass('fade')) {
											nextcaption.data('repo',nextcaption.css('opacity'));
											nextcaption.animate({'opacity':1});
										}
										if (nextcaption.hasClass('lfr') ||
											nextcaption.hasClass('lfl') ||
											nextcaption.hasClass('sfr') ||
											nextcaption.hasClass('sfl') ||
											nextcaption.hasClass('lft') ||
											nextcaption.hasClass('lfb') ||
											nextcaption.hasClass('sft') ||
											nextcaption.hasClass('sfb')
											)
										{
											var easetype=nextcaption.data('easing');
											if (easetype==undefined) easetype="linear";
											nextcaption.data('repx',nextcaption.position().left);
											nextcaption.data('repy',nextcaption.position().top);

											nextcaption.data('repo',nextcaption.css('opacity'));
											nextcaption.animate({'opacity':1,'left':(xbw*nextcaption.data('x')+offsetx)+'px','top':opt.bh*(nextcaption.data('y'))+"px"},{duration:nextcaption.data('speed'), easing:easetype});
										}
								},nextcaption.data('start')));

						})
				}



		///////////////////////////
		//	-	COUNTDOWN	-	//
		/////////////////////////
		function countDown(container,opt) {
			opt.cd=0;

			var bt=container.find('.tp-bannertimer');
			if (bt.length>0) {
				bt.css({'width':'0%'});
				bt.animate({'width':"100%"},{duration:(opt.delay-100),queue:false, easing:"linear"});
			}

			bt.data('opt',opt);
			opt.cdint=setInterval(function() {

				if (opt.conthover!=1 && opt.videoplaying!=true) opt.cd=opt.cd+100;

				// STOP TIMER IF NO LOOP NO MORE NEEDED.
			    if (opt.stopLoop=="on" && opt.act==	container.find('>ul >li').length-1) {
						clearInterval(opt.cdint);
						container.find('.tp-bannertimer').css({'visibility':'hidden'});
				}

				if (opt.cd>=opt.delay) {
					opt.cd=0;
					// SWAP TO NEXT BANNER
					opt.act=opt.next;
					opt.next=opt.next+1;
					if (opt.next>container.find('>ul >li').length-1) opt.next=0;


					// SWAP THE SLIDES
					swapSlide(container,opt);

					// Clear the Timer
					if (bt.length>0) {
						bt.css({'width':'0%'});
						bt.animate({'width':"100%"},{duration:(opt.delay-100),queue:false, easing:"linear"});
					}
				}
			},100);

			container.hover(
				function() {
					opt.conthover=1;
					if (opt.onHoverStop=="on") {
						bt.stop();
					}
				},
				function() {
					opt.conthover=0;
					if (opt.onHoverStop=="on" && opt.videoplaying!=true) {
						bt.animate({'width':"100%"},{duration:((opt.delay-opt.cd)-100),queue:false, easing:"linear"});
					}
				});
		}



})(jQuery);




