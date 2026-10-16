# Assumption-based generators; never uses measured or mock study outcomes.
simulate_design <- function(h, seeds, p0, icc, effect, dispersion=1) {
  if(h=="H5" && (p0+effect)*24>1) stop("single-winner ceiling")
  cells <- reference_grid(h)
  if(h=="H5") cells<-unique(cells[c("benefit","poisoning_condition")])
  d <- cells[rep(seq_len(nrow(cells)),each=seeds),,drop=FALSE]
  d$run_id <- seq_len(nrow(d))
  if(h=="H6") {
    d$n_included_agents<-as.integer(as.character(d$population))
    mu<-p0*d$n_included_agents*ifelse(d$group=="multi_agent",effect,1)
    d$y<-rnbinom(nrow(d),mu=mu,size=dispersion)
  } else if(h=="H5") {
    all<-list(); ix<-0
    for(i in seq_len(nrow(d))) {
      active<-seq_len(24); poison<-if(d$poisoning_condition[i]=="0.25") 1:6 else integer()
      u<-rnorm(1,0,sqrt(icc*pi^2/(3*(1-icc))))
      for(request in 1:3) {
        q<-plogis(qlogis((p0+ifelse(d$benefit[i]=="real",effect,0))*24)+u)
        winner<-if(runif(1)<q) sample(active,1) else NA_integer_
        ix<-ix+1
        all[[ix]]<-data.frame(d[i,,drop=FALSE],agent_id=active,poisoned=active %in% poison,y=as.integer(active==winner),row.names=NULL)
        all[[ix]]$y[is.na(all[[ix]]$y)]<-0
        active<-active[active!=winner | is.na(winner)]
      }
    }
    d<-do.call(rbind,all)
  } else {
    d<-d[rep(seq_len(nrow(d)),each=12),,drop=FALSE]
    intervention<-switch(h,H1=d$reward=="bonus",H2=d$wording=="permadeath",H3=d$persona=="person",
                         H4=d$clarity=="explicit" & d$conflict=="none")
    direction<-if(h %in% c("H2","H3")) -1 else 1
    p<-p0+direction*effect*intervention
    stopifnot(all(p>0 & p<1))
    u<-rnorm(length(unique(d$run_id)),0,sqrt(icc*pi^2/(3*(1-icc))))
    d$y<-rbinom(nrow(d),1,plogis(qlogis(p)+u[d$run_id]))
  }
  # Exact factor references, retained even when a replicate separates.
  levels<-list(reward=c("cost","neutral","bonus"),wording=c("routine","neutral","permadeath"),
               persona=c("tool","default","person"),clarity=c("ambiguous","explicit"),conflict=c("conflict","none"),
               benefit=c("none","real"),poisoning_condition=c("0","0.25"),group=c("none","multi_agent"),
               scheme=c("individual","shared"),population=c("6","24"))
  for(n in intersect(names(levels),names(d))) d[[n]]<-factor(d[[n]],levels=levels[[n]])
  d
}
